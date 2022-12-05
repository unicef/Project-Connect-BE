import json
import os
from datetime import datetime
from unittest.mock import patch

from django.test import TestCase

from pytz import UTC

from proco.connection_statistics.models import RealTimeConnectivity
from proco.locations.tests.factories import CountryFactory
from proco.schools.loaders.brasil_loader import brasil_statistic_loader
from proco.schools.tests.factories import SchoolFactory


class TestBrazilParser(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        with open(os.path.join('proco', 'connection_statistics', 'tests', 'data', 'brazil_example.json')) as example:
            cls.example_data = json.load(example)
        cls.country = CountryFactory(code='BR')

    @patch('proco.schools.loaders.brasil_loader.BrasilSimnetLoader.load_schools_statistic')
    def test_unknown_schools(self, load_mock):
        load_mock.return_value = self.example_data

        today = datetime.now().date()
        brasil_statistic_loader.update_statistic(today)
        self.assertEqual(RealTimeConnectivity.objects.filter(school__country=self.country).count(), 0)

    @patch('proco.schools.loaders.brasil_loader.BrasilSimnetLoader.load_schools_statistic')
    def test_data_loaded(self, load_mock):
        load_mock.return_value = self.example_data
        SchoolFactory(country=self.country, external_id=43029094)
        SchoolFactory(country=self.country, external_id=41062310)
        today = datetime.now().date()

        with self.assertNumQueries(6):
            brasil_statistic_loader.update_statistic(today)

        # records shouldn't be saved during second call, so there are less queries expected
        with self.assertNumQueries(4):
            brasil_statistic_loader.update_statistic(today)

        self.assertEqual(RealTimeConnectivity.objects.filter(school__country=self.country).count(), 3)
        self.assertListEqual(
            list(
                RealTimeConnectivity.objects.filter(
                    school__country=self.country,
                ).order_by('created').values_list('created', flat=True),
            ),
            [
                datetime(year=2020, month=9, day=15, hour=1, minute=10, second=37, tzinfo=UTC),
                datetime(year=2020, month=9, day=15, hour=5, minute=16, second=36, tzinfo=UTC),
                datetime(year=2020, month=9, day=15, hour=7, minute=16, second=36, tzinfo=UTC),
            ],
        )
