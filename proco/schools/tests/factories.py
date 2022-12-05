from django.contrib.gis.geos import GEOSGeometry

from factory import SubFactory
from factory import django as django_factory
from factory import fuzzy

from proco.locations.tests.factories import CountryFactory, LocationFactory
from proco.schools.models import School


class SchoolFactory(django_factory.DjangoModelFactory):
    name = fuzzy.FuzzyText(length=20)
    country = SubFactory(CountryFactory)
    location = SubFactory(LocationFactory)
    geopoint = GEOSGeometry('Point(1 1)')
    gps_confidence = fuzzy.FuzzyDecimal(low=0.0)
    altitude = fuzzy.FuzzyInteger(0, 10000)

    class Meta:
        model = School
