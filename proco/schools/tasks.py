import random
import traceback
from collections import Counter
from copy import copy
from random import randint  # noqa
from typing import List

from django.contrib.gis.geos import MultiPoint, Point
from django.db import transaction

from proco.connection_statistics.utils import update_country_data_source_by_csv_filename, update_country_weekly_status
from proco.locations.models import Country
from proco.schools.loaders import ingest
from proco.schools.loaders.ingest import UnsupportedFileFormatException, load_data
from proco.schools.models import FileImport
from proco.taskapp import app
from proco.utils.tasks import update_country_related_cache


class FailedImportError(Exception):
    pass


def _find_country(loaded: List[dict]) -> [Country]:
    points = MultiPoint()

    shuffled_data = copy(loaded)
    random.shuffle(shuffled_data)  # noqa

    for data in shuffled_data:
        if len(points) == 2000:
            # exit if we already collected optimal number of points to proceed
            break

        try:
            point = Point(x=float(data['lon']), y=float(data['lat']))
        except (TypeError, ValueError, KeyError):
            continue

        if point == Point(x=0, y=0):
            continue

        points.append(point)

    countries = list(Country.objects.filter(geometry__intersects=points))

    if not countries:
        return None
    elif len(countries) == 1:
        return countries[0]
    else:
        countries_counter = Counter()
        for country in countries:
            instersections = country.geometry.intersection(points)
            if isinstance(instersections, Point):
                countries_counter[country] = 1
            else:
                countries_counter[country] = len(instersections)
        return countries_counter.most_common()[0][0]


@app.task(soft_time_limit=4 * 60 * 60, time_limit=4 * 60 * 60)
def process_loaded_file(pk: int, force: bool = False):
    imported_file = FileImport.objects.filter(pk=pk).first()
    if not imported_file:
        return

    imported_file.status = FileImport.STATUSES.started
    imported_file.save()

    try:
        loaded_data = list(load_data(imported_file.uploaded_file))
        imported_file.statistic = 'Total count of rows in the file: {0}\n'.format(len(loaded_data))
        imported_file.country = _find_country(loaded_data)
        if not imported_file.country:
            imported_file.status = FileImport.STATUSES.failed
            imported_file.errors = 'Error: Country not found'
            imported_file.save()
            return

        warnings, errors, processed = [], [], 0

        try:
            with transaction.atomic():
                warnings, errors, processed = ingest.save_data(imported_file.country, loaded_data, ignore_errors=force)
                if errors and not force:
                    raise FailedImportError
                imported_file.statistic += 'Count of processed rows: {0}\n'.format(processed)
        except FailedImportError:
            imported_file.statistic += 'Count of processed rows: 0\n'

        imported_file.statistic += 'Count of bad rows: {0}\n'.format(len(errors + warnings))
        bad_rows_counter = Counter(map(lambda x: x.split(': ')[1], errors + warnings))
        imported_file.statistic += '\n'.join(
            map(lambda x: 'Total {0} schools: {1}'.format(x[1], x[0]), bad_rows_counter.most_common()),
        )
        imported_file.errors = '\n'.join(errors)
        if warnings:
            imported_file.errors += '\nWarnings:\n'
            imported_file.errors += '\n'.join(map(str, warnings))

        if errors and not force:
            imported_file.status = FileImport.STATUSES.failed
        elif errors and force:
            imported_file.status = FileImport.STATUSES.completed_with_errors
        else:
            imported_file.status = FileImport.STATUSES.completed

        imported_file.save()

        if not errors or force:
            def update_stats():
                update_country_weekly_status(imported_file.country)
                update_country_data_source_by_csv_filename(imported_file)
                imported_file.country.invalidate_country_related_cache()
                update_country_related_cache.delay(imported_file.country.code)

            transaction.on_commit(update_stats)
    except UnsupportedFileFormatException as e:
        imported_file.status = FileImport.STATUSES.failed
        imported_file.errors = str(e)
        imported_file.save()
        raise
    except Exception:  # noqa: B902
        imported_file.status = FileImport.STATUSES.failed
        imported_file.errors = traceback.format_exc()
        imported_file.save()
        raise
