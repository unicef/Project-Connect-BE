import random
from datetime import datetime

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from rest_framework import status

from proco.connection_statistics.models import CountryWeeklyStatus
from proco.connection_statistics.tests.factories import (
    CountryDailyStatusFactory,
    CountryWeeklyStatusFactory,
    SchoolWeeklyStatusFactory,
)
from proco.locations.tests.factories import CountryFactory
from proco.schools.tests.factories import SchoolFactory
from proco.utils.tests import TestAPIViewSetMixin


class GlobalStatisticsApiTestCase(TestAPIViewSetMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country_one = CountryFactory()
        cls.school_one = SchoolFactory(country=cls.country_one, location__country=cls.country_one, geopoint=None)
        cls.school_two = SchoolFactory(country=cls.country_one, location__country=cls.country_one)
        SchoolWeeklyStatusFactory(school=cls.school_one, connectivity=True)
        SchoolWeeklyStatusFactory(school=cls.school_two, connectivity=False)
        CountryWeeklyStatusFactory(country=cls.country_one, integration_status=CountryWeeklyStatus.REALTIME_MAPPED,
                                   year=datetime.now().year + 1, schools_connectivity_no=1)
        cls.cws = CountryWeeklyStatusFactory(integration_status=CountryWeeklyStatus.STATIC_MAPPED,
                                             schools_connectivity_no=0,
                                             year=datetime.now().year + 2)

    def setUp(self):
        cache.clear()
        super().setUp()

    def test_global_stats(self):
        response = self.forced_auth_req(
            'get',
            reverse('connection_statistics:global-stat'),
        )
        correct_response = {
            'total_schools': 2,
            'schools_mapped': 1,
            'percent_schools_without_connectivity': 0.5,
            'countries_joined': 2,
            'all_countries': 2,
            'schools_without_connectivity':2,            
            'countries_with_static_data': 1,
            'last_date_updated': self.cws.date.strftime('%B %Y'),
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, correct_response)

    def test_global_stats_queries(self):
        with self.assertNumQueries(6):
            self.forced_auth_req(
                'get',
                reverse('connection_statistics:global-stat'),
            )
        with self.assertNumQueries(0):
            self.forced_auth_req(
                'get',
                reverse('connection_statistics:global-stat'),
            )


class CountryWeekStatsApiTestCase(TestAPIViewSetMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country_one = CountryFactory()
        cls.country_two = CountryFactory()
        cls.stat_one = CountryWeeklyStatusFactory(country=cls.country_one)
        cls.stat_two = CountryWeeklyStatusFactory(country=cls.country_two)

    def test_country_weekly_stats(self):
        response = self.forced_auth_req(
            'get',
            reverse('connection_statistics:country-weekly-stat', kwargs={
                'country_code': self.stat_one.country.code.lower(),
                'year': self.stat_one.year,
                'week': self.stat_one.week,
            }),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['schools_total'], self.stat_one.schools_total)
        self.assertEqual(response.data['avg_distance_school'], self.stat_one.avg_distance_school)
        self.assertEqual(response.data['schools_connected'], self.stat_one.schools_connected)
        self.assertEqual(response.data['schools_connectivity_unknown'], self.stat_one.schools_connectivity_unknown)
        self.assertEqual(response.data['schools_connectivity_moderate'], self.stat_one.schools_connectivity_moderate)
        self.assertEqual(response.data['schools_connectivity_good'], self.stat_one.schools_connectivity_good)
        self.assertEqual(response.data['schools_connectivity_no'], self.stat_one.schools_connectivity_no)
        self.assertEqual(response.data['integration_status'], self.stat_one.integration_status)

    def test_country_weekly_stats_queries(self):
        code = self.stat_one.country.code.lower()
        with self.assertNumQueries(2):
            self.forced_auth_req(
                'get',
                reverse('connection_statistics:country-weekly-stat', kwargs={
                    'country_code': code,
                    'year': self.stat_one.year,
                    'week': self.stat_one.week,
                }),
            )


class CountryDailyStatsApiTestCase(TestAPIViewSetMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country_one = CountryFactory()
        cls.country_two = CountryFactory()

        cls.country_one_stats_number = random.SystemRandom().randint(a=5, b=25)
        for _i in range(cls.country_one_stats_number):
            CountryDailyStatusFactory(country=cls.country_one)

        CountryDailyStatusFactory(country=cls.country_two)

    def test_country_weekly_stats(self):
        response = self.forced_auth_req(
            'get',
            reverse('connection_statistics:country-daily-stat', kwargs={
                'country_code': self.country_one.code.lower(),
            }),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], self.country_one_stats_number)

        response = self.forced_auth_req(
            'get',
            reverse('connection_statistics:country-daily-stat', kwargs={
                'country_code': self.country_two.code.lower(),
            }),
        )
        self.assertEqual(response.data['count'], 1)

    def test_country_weekly_stats_queries(self):
        code = self.country_one.code.lower()
        with self.assertNumQueries(3):
            self.forced_auth_req(
                'get',
                reverse('connection_statistics:country-daily-stat', kwargs={
                    'country_code': code,
                }),
            )
