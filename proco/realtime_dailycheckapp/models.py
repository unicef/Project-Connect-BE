from datetime import datetime, timedelta

from django.contrib.postgres.fields import JSONField
from django.core.cache import cache
from django.db import models
from django.utils import timezone


class DailyCheckApp_MeasurementManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().using('dailycheckapp_realtime')


class DailyCheckApp_Measurement(models.Model):
    DAILYCHECKAPP_MEASUREMENT_DATE_CACHE_KEY = 'dailycheckapp_realtime_last_dailycheckapp_measurement_at'

    Timestamp = models.DateTimeField()
    UUID = models.TextField(blank=True)
    BrowserID = models.TextField(blank=True)
    school_id = models.TextField()
    DeviceType = models.TextField(blank=True)
    Notes = models.TextField(blank=True)
    ClientInfo = JSONField(default=dict)
    ServerInfo = JSONField(default=dict)
    annotation = models.TextField(blank=True)
    Download = models.FloatField(blank=True)
    Upload = models.FloatField(blank=True)
    Latency = models.IntegerField(blank=True)
    Results = JSONField(default=dict)

    objects = DailyCheckApp_MeasurementManager()

    class Meta:
        managed = False
        db_table = 'dailycheckapp_measurements'

    @classmethod
    def get_last_dailycheckapp_measurement_date(cls) -> datetime:
        last_dailycheckapp_measurement_at = cache.get(cls.DAILYCHECKAPP_MEASUREMENT_DATE_CACHE_KEY)
        if not last_dailycheckapp_measurement_at:
            return timezone.now() - timedelta(days=1)
        return last_dailycheckapp_measurement_at

    @classmethod
    def set_last_dailycheckapp_measurement_date(cls, value: datetime):
        cache.set(cls.DAILYCHECKAPP_MEASUREMENT_DATE_CACHE_KEY, value)
