from django.utils import timezone

import factory.fuzzy

from proco.realtime_dailycheckapp.models import DailyCheckApp_Measurement


class DailyCheckApp_MeasurementFactory(factory.django.DjangoModelFactory):
    Timestamp = factory.LazyFunction(lambda: timezone.now())
    UUID = factory.fuzzy.FuzzyText()
    BrowserID = factory.fuzzy.FuzzyText()
    school_id = factory.fuzzy.FuzzyText()
    DeviceType = factory.fuzzy.FuzzyText()
    Notes = factory.fuzzy.FuzzyText()
    ClientInfo = {
        'IP': '127.0.0.1',
        'City': 'Neverwinter',
        'Postal': '9999',
        'Region': 'Sword Coast North',
        'Country': 'Faerûn',
        'Latitude': 0.01,
        'Timezone': 'America/New_York',
        'Longitude': 0.01,
    }
    ServerInfo = {
        'URL': 'http://localhost:7123',
        'City': 'Icewind Dale',
        'IPv4': '127.0.0.1',
        'Label': 'New York',
        'Country': 'Faerûn',
    }
    annotation = factory.fuzzy.FuzzyText()
    Download = factory.fuzzy.FuzzyFloat(0, 10**6)
    Upload = factory.fuzzy.FuzzyFloat(0, 10**6)
    Latency = factory.fuzzy.FuzzyInteger(1, 1000)
    Results = {
        'CurMSS': '1428',
        'Timeouts': '0',
    }

    class Meta:
        model = DailyCheckApp_Measurement
