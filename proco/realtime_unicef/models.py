from datetime import datetime, timedelta

from django.contrib.postgres.fields import JSONField
from django.core.cache import cache
from django.db import models
from django.utils import timezone


class MeasurementManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().using('realtime')


class Measurement(models.Model):
    MEASUREMENT_DATE_CACHE_KEY = 'realtime_last_measurement_at'

    timestamp = models.DateTimeField()
    uuid = models.TextField(blank=True)
    browser_id = models.TextField(blank=True)
    school_id = models.TextField()
    device_type = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    client_info = JSONField(default=dict)
    server_info = JSONField(default=dict)
    annotation = models.TextField(blank=True)
    download = models.FloatField(blank=True)
    upload = models.FloatField(blank=True)
    latency = models.IntegerField(blank=True)
    results = JSONField(default=dict)

    objects = MeasurementManager()

    class Meta:
        managed = False
        db_table = 'measurements'

    @classmethod
    def get_last_measurement_date(cls) -> datetime:
        last_measurement_at = cache.get(cls.MEASUREMENT_DATE_CACHE_KEY)
        if not last_measurement_at:
            return timezone.now() - timedelta(days=1)
        return last_measurement_at

    @classmethod
    def set_last_measurement_date(cls, value: datetime):
        cache.set(cls.MEASUREMENT_DATE_CACHE_KEY, value)
