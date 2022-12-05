import logging

from django.utils import timezone

from proco.connection_statistics.models import RealTimeConnectivity
from proco.locations.models import Country
from proco.realtime_unicef.models import Measurement
from proco.schools.models import School

logger = logging.getLogger('django.' + __name__)


def sync_realtime_data():
    measurements = Measurement.objects.filter(timestamp__gt=Measurement.get_last_measurement_date())

    realtime = []

    countries = {m.client_info.get('Country') for m in measurements}
    for country_code in countries:
        if country_code:
            country = Country.objects.filter(code=country_code).first()
        else:
            country = None

        schools_qs = School.objects
        if country:
            schools_qs = schools_qs.filter(country=country)

        schools_ids = {m.school_id for m in measurements if m.client_info.get('Country') == country_code}
        schools = {
            school.external_id: school
            for school in schools_qs.filter(external_id__in=schools_ids)
        }

        for measurement in measurements:
            if measurement.school_id not in schools:
                logger.debug(f'skipping measurement {measurement.uuid}: unknown school {measurement.school_id}')
                continue

            if(measurement.download > 0 and measurement.latency > 0):
                realtime.append(RealTimeConnectivity(
                    created=measurement.timestamp,
                    connectivity_speed=measurement.download * 1024,  # kb/s -> b/s
                    connectivity_latency=measurement.latency,
                    school=schools[measurement.school_id],
                ))

    RealTimeConnectivity.objects.bulk_create(realtime)

    # not using aggregate because there can be new entries between two operations
    if measurements:
        last_update = max((m.timestamp for m in measurements))
    else:
        last_update = timezone.now()
    Measurement.set_last_measurement_date(last_update)
