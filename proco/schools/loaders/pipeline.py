import logging
from datetime import date
from typing import Iterable, List, Tuple

from django.contrib.gis.geos import Point
from django.db.models import F
from django.utils.translation import ugettext_lazy as _

from scipy.spatial import KDTree

from proco.connection_statistics.models import SchoolWeeklyStatus
from proco.locations.models import Country
from proco.schools.loaders.validation import validate_point_distance, validate_row
from proco.schools.models import School
from proco.utils.geometry import cartesian

logger = logging.getLogger('django.' + __name__)


def get_validated_rows(country: Country, loaded: Iterable[dict]) -> Tuple[List[dict], List[str], List[str]]:
    errors = []
    warnings = []
    csv_external_ids = {}
    csv_geopoints = {}
    csv_geopoints_by_type = {}
    rows = []

    for i, data in enumerate(loaded):
        row_index = i + 2  # enumerate starts from zero plus header
        # remove non-unicode symbols from keys and empty suffixes/prefixes
        data = {
            key.encode('ascii', 'ignore').decode(): value.strip() if isinstance(value, str) else value
            for key, value in data.items()
        }
        # remove empty strings from data
        # empty values check is ugly; should be refactored (like validation in overall, it has lot of duplicated code)
        data = {
            key: value
            for key, value in data.items()
            if value != '' and ((not key.startswith('admin') and value not in ['na', 'nd']) or key.startswith('admin'))
        }
        if not data:
            continue

        if i % 1000 == 0:
            logger.info(f'validated {i}')

        school_data, history_data, row_errors, row_warnings = validate_row(country, data)
        if row_errors:
            errors.extend(f'Row {row_index}: {error}' for error in row_errors)
            continue

        if row_warnings:
            warnings.extend(f'Row {row_index}: {warning}' for warning in row_warnings)
            continue

        if 'external_id' in school_data:
            external_id = school_data['external_id'].lower()
            if external_id in csv_external_ids:
                warnings.append(_(
                    f'Row {row_index}: Bad data provided for school identifier:'
                    f' duplicate entry with row {csv_external_ids[external_id]}',
                ))
                continue
            csv_external_ids[external_id] = row_index

        # if 'education_level' in school_data:
        #     education_level = school_data['education_level']
        #     if education_level not in csv_geopoints_by_type:
        #         csv_geopoints_by_type[education_level] = {}
        #     else:
        #         if school_data['geopoint'] in csv_geopoints_by_type[education_level]:
        #             warnings.append(_(
        #                 f'Row {row_index}: Bad data provided for geopoint:'
        #                 f' duplicate entry with row {csv_geopoints[school_data["geopoint"]]}',
        #             ))
        #             continue
        #
        #     csv_geopoints_by_type[education_level][school_data['geopoint']] = row_index
        # else:
        #     if school_data['geopoint'] in csv_geopoints:
        #         warnings.append(_(
        #             f'Row {row_index}: Bad data provided for geopoint:'
        #             f' duplicate entry with row {csv_geopoints[school_data["geopoint"]]}',
        #         ))
        #         continue
        #
        # csv_geopoints[school_data['geopoint']] = row_index

        rows.append({
            'row_index': row_index,
            'school_data': school_data,
            'history_data': history_data,
        })

    return rows, errors, warnings


def map_schools_by_external_id(country: Country, rows: List[dict]):
    # search by external id
    schools_with_external_id = {
        data['school_data']['external_id'].lower(): data
        for data in rows
        if 'external_id' in data['school_data']
    }
    if not schools_with_external_id:
        return

    schools_mapped = 0
    external_ids = list(schools_with_external_id.keys())
    for i in range(0, len(external_ids), 1000):
        schools_by_external_id = School.objects.filter(
            country=country,
            external_id__in=external_ids[i:min(i + 1000, len(external_ids))],
        ).select_related('last_weekly_status')
        for school in schools_by_external_id:
            schools_with_external_id[school.external_id]['school'] = school
        schools_mapped += len(schools_by_external_id)

    logger.info(f'{schools_mapped} mapped by external_id')


def map_schools_by_geopoint_and_education_level(country: Country, rows: List[dict]):
    education_levels = {
        data['school_data']['education_level']
        for data in rows
        if 'education_level' in data['school_data']
    }

    for level in education_levels:
        schools_with_geopoint = {
            data['school_data']['geopoint'].wkt: data
            for data in rows
            if 'school' not in data
               and 'education_level' in data['school_data']
               and data['school_data']['education_level'] == level
        }
        if not schools_with_geopoint:
            continue

        geopoints = [data['school_data']['geopoint'] for data in schools_with_geopoint.values()]
        schools_mapped = 0

        for i in range(0, len(geopoints), 1000):
            schools_by_geopoint = School.objects.filter(
                country=country,
                education_level=level,
                geopoint__in=geopoints[i:min(i + 1000, len(geopoints))],
            ).select_related('last_weekly_status')
            for school in schools_by_geopoint:
                schools_with_geopoint[Point(x=school.geopoint.x, y=school.geopoint.y).wkt]['school'] = school
            schools_mapped += len(schools_by_geopoint)

        logger.info(f'{schools_mapped} mapped by {len(geopoints)} geopoint with edication level {level}')


def map_schools_by_geopoint_and_empty_education_level(country: Country, rows: List[dict]):
    # if education level provided in file but not for particular schools, we can try to find them with this information
    education_level_provided = any('education_level' in data['school_data'] for data in rows)
    if not education_level_provided:
        return

    schools_with_geopoint = {
        data['school_data']['geopoint'].wkt: data
        for data in rows
        if 'school' not in data and 'education_level' not in data['school_data']
    }
    if not schools_with_geopoint:
        return

    geopoints = [data['school_data']['geopoint'] for data in schools_with_geopoint.values()]
    schools_mapped = 0

    for i in range(0, len(geopoints), 1000):
        schools_by_geopoint = School.objects.filter(
            country=country,
            education_level='',
            geopoint__in=geopoints[i:min(i + 1000, len(geopoints))],
        ).select_related('last_weekly_status')
        for school in schools_by_geopoint:
            schools_with_geopoint[Point(x=school.geopoint.x, y=school.geopoint.y).wkt]['school'] = school
        schools_mapped += len(schools_by_geopoint)

    logger.info(f'{schools_mapped} mapped by {len(geopoints)} geopoints with empty edication level')


def map_schools_by_geopoint(country: Country, rows: List[dict]):
    education_level_provided = any('education_level' in data['school_data'] for data in rows)
    if education_level_provided:
        logger.info('education level provided, regular geopoint skipped')
        return

    # search by geopoint
    schools_with_geopoint = {
        data['school_data']['geopoint'].wkt: data
        for data in rows
        if 'school' not in data
    }
    if not schools_with_geopoint:
        return

    geopoints = [data['school_data']['geopoint'] for data in schools_with_geopoint.values()]
    schools_mapped = 0

    for i in range(0, len(geopoints), 1000):
        schools_by_geopoint = School.objects.filter(
            country=country,
            geopoint__in=geopoints[i:min(i + 1000, len(geopoints))],
        ).select_related('last_weekly_status')
        for school in schools_by_geopoint:
            schools_with_geopoint[Point(x=school.geopoint.x, y=school.geopoint.y).wkt]['school'] = school
        schools_mapped += len(schools_by_geopoint)

    logger.info(f'{schools_mapped} mapped by {len(geopoints)} geopoint')


def remove_mapped_twice_schools(rows: List[dict]) -> Tuple[List[dict], List[str]]:
    warnings = []
    schools = {}
    unique_rows = []
    for data in rows:
        if 'school' not in data:
            unique_rows.append(data)
            continue

        if data['school'].id in schools:
            warnings.append(_(
                f'Row {data["row_index"]}: Duplicated data: school was'
                f' already mapped in row {schools[data["school"].id]}.'
                f' Please check external_id and geopoint',
            ))
            continue
        else:
            schools[data['school'].id] = data['row_index']
            unique_rows.append(data)

    return unique_rows, warnings


def remove_too_close_points(country: Country, rows: List[dict]) -> List[str]:
    # 1. get all possible points from schools table
    # 2. for every changed point, remove it from list and re-check it still valid
    # 3. for every new point, check it's distance from schools of similar type is greater than 500m
    # P.S. second step missing, kd-trees don't allow insertions.
    # solutions: don't allow point to be removed. pros: we can skip bad geopoint if school exists

    errors = []
    school_points = {'all': set()}

    for school in School.objects.filter(country=country).values('education_level', 'geopoint'):
        if school['education_level'] not in school_points:
            school_points[school['education_level']] = set()
        cartesian_coord = cartesian(school['geopoint'].y, school['geopoint'].x)
        school_points[school['education_level']].add(cartesian_coord)
        school_points['all'].add(cartesian_coord)

    # add all points to generate final kdtree
    for data in [d for d in rows if 'school' not in d]:
        point = data['school_data']['geopoint']
        cartesian_coord = cartesian(point.y, point.x)
        education_level = data['school_data'].get('education_level')
        if education_level:
            if education_level not in school_points:
                school_points[education_level] = set()
            school_points[education_level].add(cartesian_coord)
        school_points['all'].add(cartesian_coord)

    for key in school_points.keys():
        school_points[key] = KDTree(school_points[key])

    new_schools = [d for d in rows if 'school' not in d]

    logger.info(f'started points check, {len(rows)} items')

    bad_schools = []
    for i, data in enumerate(new_schools):
        point = data['school_data']['geopoint']
        cartesian_coord = cartesian(point.y, point.x)
        education_level = data['school_data'].get('education_level')

        if i % 1000 == 0:
            logger.info(f'processed {i} geopoints')

        if education_level:
            if not validate_point_distance(school_points[education_level], cartesian_coord):
                errors.append(_(
                    'Row {0}: Geopoint is closer than 500m to another with same education level.',
                ).format(data['row_index']))
                bad_schools.append(data)
        else:
            if not validate_point_distance(school_points['all'], cartesian_coord):
                errors.append(_(
                    'Row {0}: Geopoint is closer than 500m to another. '
                    'Please specify education_level for better search.',
                ).format(data['row_index']))
                bad_schools.append(data)

    for bad_data in bad_schools:
        rows.remove(bad_data)

    logger.info(f'finished points check, {len(rows)} items left')

    return errors


def create_new_schools(rows: List[dict]):
    # bulk create new schools
    new_schools = []
    for data in rows:
        if 'school' in data:
            continue

        school = School(**data['school_data'])
        school.name_lower = school.name.lower()
        school.external_id = school.external_id.lower()

        new_schools.append(school)
        data['school'] = school
        data['school_created'] = True

    if new_schools:
        logger.info(f'{len(new_schools)} schools will be created')
        School.objects.bulk_create(new_schools, batch_size=1000)


def update_existing_schools(rows: List[dict]):
    # bulk update existing ones
    all_schools_to_update = [data for data in rows if not data.get('school_created', False)]

    logger.info(f'{len(all_schools_to_update)} schools will be updated')
    fields_combinations = {tuple(sorted(data['school_data'].keys())) for data in all_schools_to_update}

    for fields_combination in fields_combinations:
        schools_to_update = []
        for data in all_schools_to_update:
            if tuple(sorted(data['school_data'].keys())) == fields_combination:
                for field in fields_combination:
                    setattr(data['school'], field, data['school_data'][field])
                schools_to_update.append(data['school'])

        logger.info(f'{len(schools_to_update)} schools will be updated with {fields_combination}')
        School.objects.bulk_update(schools_to_update, fields_combination, batch_size=1000)


def delete_schools_not_in_bounds(country: Country, rows: List[dict]) -> List[str]:
    errors = []

    # check & remove schools not in bounds. this is the fastest way
    School.objects.filter(country=country).exclude(geopoint__within=F('country__geometry')).delete()
    logger.info(f'{len(rows)} schools before filtering')

    schools_within = School.objects.filter(id__in=[d['school'].id for d in rows]).values_list('id', flat=True)
    bad_rows = []
    for data in rows:
        if data['school'].id not in schools_within:
            errors.append(_('Row {0}: Bad data provided for geopoint: point outside country').format(data['row_index']))
            bad_rows.append(data)

    for bad_row in bad_rows:
        rows.remove(bad_row)

    logger.info(f'{len(bad_rows)} schools are outside boundaries')

    return errors


def update_schools_weekly_statuses(rows: List[dict]):
    year, week_number, week_day = date.today().isocalendar()
    schools_weekly_status_list = []
    updated_schools = {}

    # prepare new values for weekly statuses
    for data in rows:
        school = data['school']
        history_data = data['history_data']

        status = school.last_weekly_status
        if status:
            status.id = None
            for k, v in history_data.items():
                setattr(status, k, v)
        else:
            status = SchoolWeeklyStatus(school=school, **history_data)

        status.year = year
        status.week = week_number
        status.date = status.get_date()

        schools_weekly_status_list.append(status)
        updated_schools[school.id] = school

    # re-create weekly statuses with new data
    if schools_weekly_status_list:
        # use protected method here to bypass models layer. we don't want to set null in every school separately
        School.objects.filter(id__in=updated_schools.keys()).update(last_weekly_status=None)
        SchoolWeeklyStatus.objects.filter(
            school_id__in=updated_schools.keys(), year=year, week=week_number,
        )._raw_delete(SchoolWeeklyStatus.objects.db)
        SchoolWeeklyStatus.objects.bulk_create(schools_weekly_status_list, batch_size=1000)

        # set last weekly id to correct one; signals don't work when batch performed
        for status in schools_weekly_status_list:
            updated_schools[status.school_id].last_weekly_status = status
        School.objects.bulk_update(updated_schools.values(), ['last_weekly_status'], batch_size=1000)

        logger.info(f'updated weekly statuses for {len(schools_weekly_status_list)} schools')

    return len(schools_weekly_status_list)
