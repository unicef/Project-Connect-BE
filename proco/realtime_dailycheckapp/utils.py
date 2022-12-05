import logging

from django.utils import timezone

from proco.connection_statistics.models import RealTimeConnectivity
from proco.locations.models import Country
from proco.realtime_dailycheckapp.models import DailyCheckApp_Measurement
from proco.schools.models import School

logger = logging.getLogger('django.' + __name__)


def sync_dailycheckapp_realtime_data():
    dailycheckapp_measurements = DailyCheckApp_Measurement.objects.filter(Timestamp__gt=DailyCheckApp_Measurement.get_last_dailycheckapp_measurement_date())

    realtime = []

    countries = {m.ClientInfo.get('Country') for m in dailycheckapp_measurements}
    for country_code in countries:
        if country_code:
            country = Country.objects.filter(code=country_code).first()
        else:
            country = None

        schools_qs = School.objects
        if country:
            schools_qs = schools_qs.filter(country=country)

        schools_ids = {m.school_id for m in dailycheckapp_measurements if m.ClientInfo.get('Country') == country_code}
        schools = {
            school.external_id: school
            for school in schools_qs.filter(external_id__in=schools_ids)
        }

        for dailycheckapp_measurement in dailycheckapp_measurements:
            if dailycheckapp_measurement.school_id not in schools:
                logger.debug(f'skipping dailycheckapp_measurement {dailycheckapp_measurement.UUID}: unknown school {dailycheckapp_measurement.school_id}')
                continue

            realtime.append(RealTimeConnectivity(
                created=dailycheckapp_measurement.Timestamp,
                connectivity_speed=dailycheckapp_measurement.Download * 1024,  # kb/s -> b/s
                connectivity_latency=dailycheckapp_measurement.Latency,
                school=schools[dailycheckapp_measurement.school_id],
            ))

    RealTimeConnectivity.objects.bulk_create(realtime)

    # not using aggregate because there can be new entries between two operations
    if dailycheckapp_measurements:
        last_update = max((m.Timestamp for m in dailycheckapp_measurements))
    else:
        last_update = timezone.now()
    DailyCheckApp_Measurement.set_last_dailycheckapp_measurement_date(last_update)
