from datetime import timedelta

from django.core.cache import cache
from django.db.models import Sum
from django.test import TestCase
from django.utils import timezone

from proco.connection_statistics.models import RealTimeConnectivity
from proco.realtime_unicef.models import Measurement
from proco.realtime_unicef.tests.db.test import init_test_db
from proco.realtime_unicef.tests.factories import MeasurementFactory
from proco.realtime_unicef.utils import sync_realtime_data
from proco.schools.tests.factories import SchoolFactory


class SyncTestCase(TestCase):
    databases = ['default', 'realtime']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        init_test_db()

    def setUp(self) -> None:
        super().setUp()
        cache.delete(Measurement.MEASUREMENT_DATE_CACHE_KEY)

    def test_empty_cache(self):
        school = SchoolFactory(external_id='test_1')
        MeasurementFactory(timestamp=timezone.now() - timedelta(days=1, hours=1), school_id='test_1', download=1)
        MeasurementFactory(timestamp=timezone.now() - timedelta(hours=23), school_id='test_1', download=2)

        sync_realtime_data()

        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 1)
        self.assertEqual(RealTimeConnectivity.objects.first().school, school)
        self.assertEqual(RealTimeConnectivity.objects.aggregate(speed=Sum('connectivity_speed'))['speed'], 2048)

        self.assertGreater(Measurement.get_last_measurement_date(), timezone.now() - timedelta(hours=23, seconds=5))

    def test_cached_measurement_date(self):
        SchoolFactory(external_id='test_1')
        MeasurementFactory(timestamp=timezone.now() - timedelta(days=1, hours=1), school_id='test_1', download=1)
        MeasurementFactory(timestamp=timezone.now() - timedelta(hours=23), school_id='test_1', download=2)

        Measurement.set_last_measurement_date(timezone.now() - timedelta(days=1, hours=2))

        sync_realtime_data()

        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 2)
        self.assertEqual(RealTimeConnectivity.objects.aggregate(speed=Sum('connectivity_speed'))['speed'], 3072)

    def test_idempotency(self):
        SchoolFactory(external_id='test_1')
        MeasurementFactory(school_id='test_1', download=1)
        MeasurementFactory(school_id='test_1', download=2)

        # two objects synchronized because they added after default last measurement date (day ago)
        sync_realtime_data()
        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 2)

        # no new entries added, because they are already synchronized
        RealTimeConnectivity.objects.all().delete()
        sync_realtime_data()
        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 0)

        # two previous entries synchronized again as we moved date back
        Measurement.set_last_measurement_date(timezone.now() - timedelta(hours=1))
        sync_realtime_data()
        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 2)

    def test_school_matching(self):
        school = SchoolFactory(external_id='test_1')
        Measurement.set_last_measurement_date(timezone.now() - timedelta(seconds=1))
        MeasurementFactory(school_id='test_1')
        sync_realtime_data()
        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 1)
        self.assertEqual(RealTimeConnectivity.objects.first().school, school)

    def test_school_matching_external_id_collision(self):
        SchoolFactory(external_id='test_1')
        school = SchoolFactory(external_id='test_1', country__code='US', country__name='United States')
        SchoolFactory(external_id='test_1')

        Measurement.set_last_measurement_date(timezone.now() - timedelta(seconds=1))
        measurement = MeasurementFactory(school_id='test_1')
        measurement.client_info['Country'] = 'US'
        measurement.save()

        sync_realtime_data()

        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 1)
        self.assertEqual(RealTimeConnectivity.objects.first().school, school)

    def test_school_matching_without_client_info(self):
        # last school will be used cause to mapping logic
        SchoolFactory(external_id='test_1')
        school = SchoolFactory(external_id='test_1')

        Measurement.set_last_measurement_date(timezone.now() - timedelta(seconds=1))
        measurement = MeasurementFactory(school_id='test_1')
        measurement.client_info = {}
        measurement.save()

        sync_realtime_data()

        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 1)
        self.assertEqual(RealTimeConnectivity.objects.first().school, school)

    def test_school_matching_unknown(self):
        SchoolFactory(external_id='test_1')
        Measurement.set_last_measurement_date(timezone.now() - timedelta(seconds=1))
        MeasurementFactory()
        sync_realtime_data()
        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 0)

    def test_fields(self):
        school = SchoolFactory(external_id='test_1')
        Measurement.set_last_measurement_date(timezone.now() - timedelta(seconds=1))

        measurement = MeasurementFactory(school_id='test_1')
        sync_realtime_data()

        connectivity_info = RealTimeConnectivity.objects.first()
        self.assertIsNotNone(connectivity_info)

        self.assertEqual(RealTimeConnectivity.objects.first().created, measurement.timestamp)
        self.assertEqual(RealTimeConnectivity.objects.first().connectivity_speed, int(measurement.download * 1024))
        self.assertEqual(RealTimeConnectivity.objects.first().connectivity_latency, measurement.latency)
        self.assertEqual(RealTimeConnectivity.objects.first().school, school)
