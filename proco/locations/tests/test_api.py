from django.contrib.gis.geos import GEOSGeometry
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from rest_framework import status

from proco.connection_statistics.tests.factories import CountryWeeklyStatusFactory
from proco.locations.tests.factories import CountryFactory
from proco.schools.tests.factories import SchoolFactory
from proco.utils.tests import TestAPIViewSetMixin


class CountryApiTestCase(TestAPIViewSetMixin, TestCase):
    base_view = 'locations:countries'

    def get_detail_args(self, instance):
        return self.get_list_args() + [instance.code.lower()]

    @classmethod
    def setUpTestData(cls):
        cls.country_one = CountryFactory()
        cls.country_two = CountryFactory()
        SchoolFactory(country=cls.country_one, location__country=cls.country_one)
        SchoolFactory(country=cls.country_one, location__country=cls.country_one)
        CountryWeeklyStatusFactory(country=cls.country_one)

    def setUp(self):
        cache.clear()
        super().setUp()

    def test_countries_list(self):
        with self.assertNumQueries(1):
            response = self._test_list(
                user=None, expected_objects=[self.country_one, self.country_two],
            )
        self.assertIn('integration_status', response.data[0])

    def test_country_detail(self):
        with self.assertNumQueries(1):
            response = self._test_retrieve(
                user=None, instance=self.country_one,
            )
        self.assertIn('statistics', response.data)

    def test_country_list_cached(self):
        with self.assertNumQueries(1):
            self._test_list(
                user=None, expected_objects=[self.country_one, self.country_two],
            )

        with self.assertNumQueries(0):
            self._test_list(
                user=None, expected_objects=[self.country_one, self.country_two],
            )

    def test_empty_countries_hidden(self):
        CountryFactory(geometry=GEOSGeometry('{"type": "MultiPolygon", "coordinates": []}'))
        self._test_list(
            user=None, expected_objects=[self.country_one, self.country_two],
        )


class CountryBoundaryApiTestCase(TestAPIViewSetMixin, TestCase):
    base_view = 'locations:countries-boundary'

    @classmethod
    def setUpTestData(cls):
        cls.country_one = CountryFactory()
        cls.country_two = CountryFactory()
        SchoolFactory(country=cls.country_one, location__country=cls.country_one)
        SchoolFactory(country=cls.country_one, location__country=cls.country_one)

    def setUp(self):
        cache.clear()
        super().setUp()

    def test_countries_list(self):
        with self.assertNumQueries(1):
            response = self.forced_auth_req('get', reverse(self.base_view))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('geometry_simplified', response.data[0])

    def test_country_list_cached(self):
        with self.assertNumQueries(1):
            response = self.forced_auth_req('get', reverse(self.base_view))
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.assertNumQueries(0):
            response = self.forced_auth_req('get', reverse(self.base_view))
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_empty_countries_hidden(self):
        CountryFactory(geometry=GEOSGeometry('{"type": "MultiPolygon", "coordinates": []}'))
        response = self.forced_auth_req('get', reverse(self.base_view))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual([r['id'] for r in response.data], [self.country_one.id, self.country_two.id])
