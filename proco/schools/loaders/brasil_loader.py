from django.contrib.gis.geos import Point
from django.utils import timezone
from django.utils.functional import cached_property

import requests
from dateutil import parser as dateutil_parser
from pytz import UTC

from proco.connection_statistics.models import RealTimeConnectivity, SchoolWeeklyStatus
from proco.locations.models import Country
from proco.schools.models import School
from proco.utils.dates import get_current_week, get_current_year


class BrasilSimnetLoader(object):
    base_url = 'https://api.simet.nic.br/'

    @cached_property
    def country(self):
        return Country.objects.get(code='BR')

    def load_schools(self):
        response = requests.get('{0}school-measures/v1/getSchools'.format(self.base_url))
        return response.json()

    def save_school(self, school_data):
        required_fields = {'LNG', 'LAT', 'CO_ENTIDADE', 'NO_ENTIDADE'}

        if required_fields - set(school_data.keys()) == set():
            brasil_environment_map = {
                'urbana': 'urban',
                'rural': 'rural',
            }
            environment = school_data.get('TP_LOCALIZACAO', '').lower()
            environment = brasil_environment_map.get(environment, environment)

            school, created = School.objects.update_or_create(
                external_id=school_data['CO_ENTIDADE'],
                country=self.country,
                defaults={
                    'name': school_data['NO_ENTIDADE'],
                    'geopoint': Point(x=school_data['LNG'], y=school_data['LAT']),
                    'environment': environment,
                    'admin_1_name': school_data.get('NM_ESTADO', ''),
                    'admin_4_name': school_data.get('NM_MUNICIP', ''),
                },
            )

            date = timezone.now().date()
            school_weekly = SchoolWeeklyStatus.objects.filter(
                school=school, week=date.isocalendar()[1], year=date.isocalendar()[0],
            ).last()

            if not school_weekly:
                school_weekly = SchoolWeeklyStatus.objects.filter(school=school).last()

                if school_weekly:
                    # copy latest available one
                    school_weekly.id = None
                    school_weekly.year = get_current_year()
                    school_weekly.week = get_current_week()
                else:
                    school_weekly = SchoolWeeklyStatus.objects.create(
                        school=school,
                        year=get_current_year(),
                        week=get_current_week(),
                    )

            school_weekly.connectivity = True
            school_weekly.computer_lab = bool(int(float(school_data.get('QT_COMP_ALUNO', 0))))
            school_weekly.num_computers = int(float(school_data.get('QT_COMPUTADOR', 0)))
            school_weekly.connectivity_type = school_data.get(
                'TIPO_TECNOLOGIA', SchoolWeeklyStatus._meta.get_field('connectivity_type').default,
            )
            school_weekly.save()

    def update_schools(self):
        schools = self.load_schools()

        for school in schools:
            self.save_school(school)

    def load_schools_statistic(self, date):
        response = requests.get(
            '{0}school-measures/v1/getMeasuresbyDayofYear?dayofyear={1}'.format(self.base_url, date),
        )
        return response.json()

    def update_statistic(self, date=None):
        if date is None:
            date = timezone.now().date()

        statistic = self.load_schools_statistic(date)

        new_entries = []
        schools = {}
        last_schools_data = {}
        for data in statistic:
            if 'school_code' not in data or 'time' not in data or 'tcp_down_median_mbps' not in data:
                continue

            code = data['school_code']
            if code in schools:
                school = schools[code]
            else:
                school = School.objects.filter(country=self.country, external_id=data['school_code']).first()
                schools[code] = school

            if not school:
                continue

            entry_time = dateutil_parser.parse(data['time']).replace(tzinfo=UTC)
            if school.id not in last_schools_data:
                latest_school_entry = school.realtime_status.order_by('created').last()
                if latest_school_entry:
                    last_schools_data[school.id] = latest_school_entry.created
                else:
                    last_schools_data[school.id] = entry_time.replace(hour=0, minute=0, second=0)

            if entry_time <= last_schools_data[school.id]:
                # record already saved
                continue

            connectivity_speed = data.get('tcp_down_median_mbps', None)
            if connectivity_speed:
                # convert Mbps to bps
                connectivity_speed = connectivity_speed * 10 ** 6

            new_entries.append(
                RealTimeConnectivity(
                    created=entry_time, school=school,
                    connectivity_speed=connectivity_speed,
                    connectivity_latency=data.get('rtt_median_ms', None),
                ),
            )

            if len(new_entries) == 5000:
                RealTimeConnectivity.objects.bulk_create(new_entries)
                new_entries = []

        if len(new_entries) > 0:
            RealTimeConnectivity.objects.bulk_create(new_entries)


brasil_statistic_loader = BrasilSimnetLoader()
