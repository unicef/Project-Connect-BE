from datetime import date

from factory import SubFactory
from factory import django as django_factory
from factory import fuzzy

from proco.connection_statistics.models import (
    CountryDailyStatus,
    CountryWeeklyStatus,
    RealTimeConnectivity,
    SchoolDailyStatus,
    SchoolWeeklyStatus,
)
from proco.locations.tests.factories import CountryFactory
from proco.schools.tests.factories import SchoolFactory


class RealTimeConnectivityFactory(django_factory.DjangoModelFactory):
    school = SubFactory(SchoolFactory)
    connectivity_speed = fuzzy.FuzzyInteger(1, 1000000)
    connectivity_latency = fuzzy.FuzzyInteger(1, 100)

    class Meta:
        model = RealTimeConnectivity


class CountryDailyStatusFactory(django_factory.DjangoModelFactory):
    country = SubFactory(CountryFactory)
    date = fuzzy.FuzzyDate(date(year=1970, month=1, day=1))
    connectivity_speed = fuzzy.FuzzyInteger(1, 1000000)
    connectivity_latency = fuzzy.FuzzyInteger(1, 100)

    class Meta:
        model = CountryDailyStatus


class SchoolDailyStatusFactory(django_factory.DjangoModelFactory):
    school = SubFactory(SchoolFactory)
    date = fuzzy.FuzzyDate(date(year=1970, month=1, day=1))
    connectivity_speed = fuzzy.FuzzyInteger(1, 1000000)
    connectivity_latency = fuzzy.FuzzyInteger(1, 100)

    class Meta:
        model = SchoolDailyStatus


class CountryWeeklyStatusFactory(django_factory.DjangoModelFactory):
    country = SubFactory(CountryFactory)
    year = fuzzy.FuzzyInteger(1900, 2200)
    week = fuzzy.FuzzyInteger(1, 53)
    schools_connected = fuzzy.FuzzyInteger(0, 1000)
    schools_connectivity_unknown = fuzzy.FuzzyInteger(0, 1000)
    schools_connectivity_no = fuzzy.FuzzyInteger(0, 1000)
    schools_connectivity_moderate = fuzzy.FuzzyInteger(0, 1000)
    schools_connectivity_good = fuzzy.FuzzyInteger(0, 1000)
    connectivity_speed = fuzzy.FuzzyInteger(1, 1000000)
    integration_status = fuzzy.FuzzyChoice(dict(CountryWeeklyStatus.INTEGRATION_STATUS_TYPES).keys())
    avg_distance_school = fuzzy.FuzzyFloat(0.0, 1000.0)

    class Meta:
        model = CountryWeeklyStatus


class SchoolWeeklyStatusFactory(django_factory.DjangoModelFactory):
    school = SubFactory(SchoolFactory)
    year = fuzzy.FuzzyInteger(1900, 2200)
    week = fuzzy.FuzzyInteger(1, 53)

    connectivity_type = fuzzy.FuzzyText(length=64)
    connectivity_speed = fuzzy.FuzzyInteger(1, 1000000)
    connectivity_latency = fuzzy.FuzzyInteger(1, 100)

    class Meta:
        model = SchoolWeeklyStatus
