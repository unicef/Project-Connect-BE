from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from rest_framework import status

from proco.connection_statistics.models import CountryWeeklyStatus
from proco.connection_statistics.tests.factories import SchoolWeeklyStatusFactory
from proco.locations.tests.factories import CountryFactory
from proco.schools.tests.factories import SchoolFactory
from proco.utils.tests import TestAPIViewSetMixin


class SchoolsApiTestCase(TestAPIViewSetMixin, TestCase):
    base_view = 'schools:schools'

    @classmethod
    def setUpTestData(cls):
        cls.country = CountryFactory()
        cls.school_one = SchoolFactory(country=cls.country, location__country=cls.country)
        cls.school_two = SchoolFactory(country=cls.country, location__country=cls.country)
        cls.school_three = SchoolFactory(country=cls.country, location__country=cls.country)
        cls.school_weekly_one = SchoolWeeklyStatusFactory(
            school=cls.school_one,
            connectivity=True, connectivity_speed=3 * (10 ** 6),
            coverage_availability=True, coverage_type='3g',
        )
        cls.school_weekly_two = SchoolWeeklyStatusFactory(
            school=cls.school_one,
            connectivity=False, connectivity_speed=None,
            coverage_availability=False, coverage_type='no',
        )
        cls.school_weekly_three = SchoolWeeklyStatusFactory(
            school=cls.school_one,
            connectivity=None, connectivity_speed=None,
            coverage_availability=None, coverage_type='unknown',
        )
        cls.school_one.last_weekly_status = cls.school_weekly_one
        cls.school_one.save()
        cls.school_two.last_weekly_status = cls.school_weekly_two
        cls.school_two.save()
        cls.school_three.last_weekly_status = cls.school_weekly_three
        cls.school_three.save()

    def setUp(self):
        cache.clear()
        super().setUp()

    def test_schools_list(self):
        with self.assertNumQueries(2):
            response = self.forced_auth_req(
                'get',
                reverse('schools:schools-list', args=[self.country.code.lower()]),
                user=None,
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('connectivity_status', response.data[0])
            self.assertIn('coverage_status', response.data[0])
            self.assertIn('is_verified', response.data[0])

    def test_schools_list_with_part_availability(self):
        connectivity_availability = CountryWeeklyStatus.CONNECTIVITY_TYPES_AVAILABILITY.connectivity
        self.country.last_weekly_status.connectivity_availability = connectivity_availability
        coverage_availability = CountryWeeklyStatus.COVERAGE_TYPES_AVAILABILITY.coverage_availability
        self.country.last_weekly_status.coverage_availability = coverage_availability
        self.country.last_weekly_status.save()
        response = self.forced_auth_req(
            'get',
            reverse('schools:schools-list', args=[self.country.code.lower()]),
            user=None,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('connectivity_status', response.data[0])
        self.assertIn('coverage_status', response.data[0])
        self.assertEqual(response.data[0]['connectivity_status'], 'good')
        self.assertEqual(response.data[0]['coverage_status'], 'good')
        self.assertEqual(response.data[1]['connectivity_status'], 'no')
        self.assertEqual(response.data[1]['coverage_status'], 'no')
        self.assertEqual(response.data[2]['connectivity_status'], 'unknown')
        self.assertEqual(response.data[2]['coverage_status'], 'unknown')

    def test_schools_list_with_full_availability(self):
        connectivity_availability = CountryWeeklyStatus.CONNECTIVITY_TYPES_AVAILABILITY.realtime_speed
        self.country.last_weekly_status.connectivity_availability = connectivity_availability
        coverage_availability = CountryWeeklyStatus.COVERAGE_TYPES_AVAILABILITY.coverage_type
        self.country.last_weekly_status.coverage_availability = coverage_availability

        self.country.last_weekly_status.save()
        response = self.forced_auth_req(
            'get',
            reverse('schools:schools-list', args=[self.country.code.lower()]),
            user=None,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('connectivity_status', response.data[0])
        self.assertIn('coverage_status', response.data[0])
        self.assertEqual(response.data[0]['connectivity_status'], 'moderate')
        self.assertEqual(response.data[0]['coverage_status'], 'good')
        self.assertEqual(response.data[1]['connectivity_status'], 'unknown')
        self.assertEqual(response.data[1]['coverage_status'], 'no')
        self.assertEqual(response.data[2]['connectivity_status'], 'unknown')
        self.assertEqual(response.data[2]['coverage_status'], 'unknown')

    def test_authorization_user(self):
        response = self.forced_auth_req(
            'get',
            reverse('schools:schools-list', args=[self.country.code.lower()]),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_schools_detail(self):
        with self.assertNumQueries(2):
            response = self.forced_auth_req(
                'get',
                reverse('schools:schools-detail', args=[self.country.code.lower(), self.school_one.id]),
                user=None,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.school_one.id)
        self.assertIn('statistics', response.data)

    def test_update_keys(self):
        # todo: move me to proper place
        from proco.locations.models import Country
        from proco.utils.tasks import update_cached_value
        for country in Country.objects.all():
            update_cached_value(url=reverse('locations:countries-detail', kwargs={'pk': country.code.lower()}))
            update_cached_value(url=reverse('schools:schools-list', kwargs={'country_code': country.code.lower()}))

        self.assertListEqual(
            list(sorted(cache.keys('*'))),  # noqa: C413
            list(sorted([  # noqa: C413
                f'SOFT_CACHE_COUNTRY_INFO_pk_{self.country.code.lower()}',
                f'SOFT_CACHE_SCHOOLS_{self.country.code.lower()}_',
            ])),
        )
