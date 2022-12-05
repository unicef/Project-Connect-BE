from datetime import timedelta

from django.core.cache import cache
from django.db.models import Sum
from django.test import TestCase
from django.utils import timezone

from proco.connection_statistics.models import RealTimeConnectivity
from proco.realtime_dailycheckapp.models import DailyCheckApp_Measurement
from proco.realtime_dailycheckapp.tests.db.test import init_test_db
from proco.realtime_dailycheckapp.tests.factories import DailyCheckApp_MeasurementFactory
from proco.realtime_dailycheckapp.utils import sync_dailycheckapp_realtime_data
from proco.schools.tests.factories import SchoolFactory


class SyncTestCase(TestCase):
    databases = ['default', 'realtime', 'dailycheckapp_realtime']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        init_test_db()

    def setUp(self) -> None:
        super().setUp()
        cache.delete(DailyCheckApp_Measurement.DAILYCHECKAPP_MEASUREMENT_DATE_CACHE_KEY)

    def test_empty_cache(self):
        school = SchoolFactory(external_id='test_1')
        DailyCheckApp_MeasurementFactory(Timestamp=timezone.now() - timedelta(days=1, hours=1), school_id='test_1', download=1)
        DailyCheckApp_MeasurementFactory(Timestamp=timezone.now() - timedelta(hours=23), school_id='test_1', download=2)

        sync_dailycheckapp_realtime_data()

        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 1)
        self.assertEqual(RealTimeConnectivity.objects.first().school, school)
        self.assertEqual(RealTimeConnectivity.objects.aggregate(speed=Sum('connectivity_speed'))['speed'], 2048)

        self.assertGreater(DailyCheckApp_Measurement.get_last_dailycheckapp_measurement_date(), timezone.now() - timedelta(hours=23, seconds=5))

    def test_cached_dailycheckapp_measurement_date(self):
        SchoolFactory(external_id='test_1')
        DailyCheckApp_MeasurementFactory(Timestamp=timezone.now() - timedelta(days=1, hours=1), school_id='test_1', download=1)
        DailyCheckApp_MeasurementFactory(Timestamp=timezone.now() - timedelta(hours=23), school_id='test_1', download=2)

        DailyCheckApp_Measurement.set_last_dailycheckapp_measurement_date(timezone.now() - timedelta(days=1, hours=2))

        sync_dailycheckapp_realtime_data()

        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 2)
        self.assertEqual(RealTimeConnectivity.objects.aggregate(speed=Sum('connectivity_speed'))['speed'], 3072)

    def test_idempotency(self):
        SchoolFactory(external_id='test_1')
        DailyCheckApp_MeasurementFactory(school_id='test_1', download=1)
        DailyCheckApp_MeasurementFactory(school_id='test_1', download=2)

        # two objects synchronized because they added after default last dailycheckapp_measurement date (day ago)
        sync_dailycheckapp_realtime_data()
        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 2)

        # no new entries added, because they are already synchronized
        RealTimeConnectivity.objects.all().delete()
        sync_dailycheckapp_realtime_data()
        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 0)

        # two previous entries synchronized again as we moved date back
        DailyCheckApp_Measurement.set_last_dailycheckapp_measurement_date(timezone.now() - timedelta(hours=1))
        sync_dailycheckapp_realtime_data()
        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 2)

    def test_school_matching(self):
        school = SchoolFactory(external_id='test_1')
        DailyCheckApp_Measurement.set_last_dailycheckapp_measurement_date(timezone.now() - timedelta(seconds=1))
        DailyCheckApp_MeasurementFactory(school_id='test_1')
        sync_dailycheckapp_realtime_data()
        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 1)
        self.assertEqual(RealTimeConnectivity.objects.first().school, school)

    def test_school_matching_external_id_collision(self):
        SchoolFactory(external_id='test_1')
        school = SchoolFactory(external_id='test_1', country__code='US', country__name='United States')
        SchoolFactory(external_id='test_1')

        DailyCheckApp_Measurement.set_last_dailycheckapp_measurement_date(timezone.now() - timedelta(seconds=1))
        dailycheckapp_measurement = DailyCheckApp_MeasurementFactory(school_id='test_1')
        dailycheckapp_measurement.ClientInfo['Country'] = 'US'
        dailycheckapp_measurement.save()

        sync_dailycheckapp_realtime_data()

        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 1)
        self.assertEqual(RealTimeConnectivity.objects.first().school, school)

    def test_school_matching_without_client_info(self):
        # last school will be used cause to mapping logic
        SchoolFactory(external_id='test_1')
        school = SchoolFactory(external_id='test_1')

        DailyCheckApp_Measurement.set_last_dailycheckapp_measurement_date(timezone.now() - timedelta(seconds=1))
        dailycheckapp_measurement = DailyCheckApp_MeasurementFactory(school_id='test_1')
        dailycheckapp_measurement.ClientInfo = {}
        dailycheckapp_measurement.save()

        sync_dailycheckapp_realtime_data()

        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 1)
        self.assertEqual(RealTimeConnectivity.objects.first().school, school)

    def test_school_matching_unknown(self):
        SchoolFactory(external_id='test_1')
        DailyCheckApp_Measurement.set_last_dailycheckapp_measurement_date(timezone.now() - timedelta(seconds=1))
        DailyCheckApp_MeasurementFactory()
        sync_dailycheckapp_realtime_data()
        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 0)

    def test_fields(self):
        school = SchoolFactory(external_id='test_1')
        DailyCheckApp_Measurement.set_last_dailycheckapp_measurement_date(timezone.now() - timedelta(seconds=1))

        dailycheckapp_measurement = DailyCheckApp_MeasurementFactory(school_id='test_1')
        sync_dailycheckapp_realtime_data()

        connectivity_info = RealTimeConnectivity.objects.first()
        self.assertIsNotNone(connectivity_info)

        self.assertEqual(RealTimeConnectivity.objects.first().created, dailycheckapp_measurement.Timestamp)
        self.assertEqual(RealTimeConnectivity.objects.first().connectivity_speed, int(dailycheckapp_measurement.Download * 1024))
        self.assertEqual(RealTimeConnectivity.objects.first().connectivity_latency, dailycheckapp_measurement.Latency)
        self.assertEqual(RealTimeConnectivity.objects.first().school, school)
