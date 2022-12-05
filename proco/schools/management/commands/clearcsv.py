import csv

from django.contrib.gis.geos import Point
from django.core.management import BaseCommand

from proco.schools.models import School


class Command(BaseCommand):
    help = 'Clear the csv file from erroneous lines.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_name', type=str)

    def handle(self, *args, **options):
        csv_file_name = options.get('csv_file_name')

        with open(
            csv_file_name + '.csv', 'r', encoding='utf-8',
        ) as input_, open(
            csv_file_name + '_validate.csv', 'w',
        ) as output_:

            writer = csv.writer(output_)
            for i, row in enumerate(csv.DictReader(input_)):
                if i == 0:
                    writer.writerow(row)

                data = {key.encode('ascii', 'ignore').decode(): value for key, value in row.items() if value != ''}

                if not data:
                    continue

                required_fields = {'name', 'lat', 'lon'}
                missing_fields = required_fields.difference(set(data.keys()))
                if missing_fields:
                    continue

                if 'school_id' in data:
                    if len(data['school_id']) > School._meta.get_field('external_id').max_length:
                        continue

                try:
                    geopoint = Point(x=float(data['lon']), y=float(data['lat']))
                    if geopoint == Point(x=0, y=0):
                        continue

                except (TypeError, ValueError):
                    continue

                if 'speed_connectivity' in data:
                    try:
                        float(data['speed_connectivity'])
                    except ValueError:
                        continue

                if 'num_students' in data:
                    if not data['num_students'].isdigit():
                        continue
                if 'num_teachers' in data:
                    if not data['num_teachers'].isdigit():
                        continue
                if 'num_classroom' in data:
                    if not data['num_classroom'].isdigit():
                        continue
                if 'num_latrines' in data:
                    if not data['num_latrines'].isdigit():
                        continue
                if 'latency_connectivity' in data:
                    if not data['latency_connectivity'].isdigit():
                        continue

                writer.writerow(row.values())
