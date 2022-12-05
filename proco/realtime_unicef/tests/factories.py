from django.utils import timezone

import factory.fuzzy

from proco.realtime_unicef.models import Measurement


class MeasurementFactory(factory.django.DjangoModelFactory):
    timestamp = factory.LazyFunction(lambda: timezone.now())
    uuid = factory.fuzzy.FuzzyText()
    browser_id = factory.fuzzy.FuzzyText()
    school_id = factory.fuzzy.FuzzyText()
    device_type = factory.fuzzy.FuzzyText()
    notes = factory.fuzzy.FuzzyText()
    client_info = {
        'IP': '127.0.0.1',
        'City': 'Neverwinter',
        'Postal': '9999',
        'Region': 'Sword Coast North',
        'Country': 'Faerûn',
        'Latitude': 0.01,
        'Timezone': 'America/New_York',
        'Longitude': 0.01,
    }
    server_info = {
        'URL': 'http://localhost:7123',
        'City': 'Icewind Dale',
        'IPv4': '127.0.0.1',
        'Label': 'New York',
        'Country': 'Faerûn',
    }
    annotation = factory.fuzzy.FuzzyText()
    download = factory.fuzzy.FuzzyFloat(0, 10**6)
    upload = factory.fuzzy.FuzzyFloat(0, 10**6)
    latency = factory.fuzzy.FuzzyInteger(1, 1000)
    results = {
        'CurMSS': '1428',
        'Timeouts': '0',
    }

    class Meta:
        model = Measurement
