from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _

from isoweek import Week
from model_utils import Choices
from model_utils.models import TimeStampedModel

from proco.locations.models import Country
from proco.schools.constants import statuses_schema
from proco.schools.models import School
from proco.utils.dates import get_current_week, get_current_year
from proco.utils.models import ApproxQuerySet


class ConnectivityStatistics(models.Model):
    connectivity_speed = models.PositiveIntegerField(help_text=_('bps'), blank=True, null=True, default=None)
    connectivity_latency = models.PositiveSmallIntegerField(help_text=_('ms'), blank=True, null=True, default=None)

    class Meta:
        abstract = True


class CountryWeeklyStatus(ConnectivityStatistics, TimeStampedModel, models.Model):
    JOINED = 0
    SCHOOL_MAPPED = 1
    STATIC_MAPPED = 2
    REALTIME_MAPPED = 3
    COUNTRY_CREATED = 4
    SCHOOL_OSM_MAPPED = 5

    INTEGRATION_STATUS_TYPES = Choices(
        (COUNTRY_CREATED, _('Default Country Status')),
        (SCHOOL_OSM_MAPPED, _('School OSM locations mapped')),
        (JOINED, _('Country Joined Project Connect')),
        (SCHOOL_MAPPED, _('School locations mapped')),
        (STATIC_MAPPED, _('Static connectivity mapped')),
        (REALTIME_MAPPED, _('Real time connectivity mapped')),
    )
    CONNECTIVITY_TYPES_AVAILABILITY = Choices(
        ('no_connectivity', _('No data')),
        ('connectivity', _('Using availability information')),
        ('static_speed', _('Using actual static speeds')),
        ('realtime_speed', _('Using actual realtime speeds')),
    )
    COVERAGE_TYPES_AVAILABILITY = Choices(
        ('no_coverage', _('No data')),
        ('coverage_availability', _('Using availability information')),
        ('coverage_type', _('Using actual coverage type')),
    )

    country = models.ForeignKey(Country, related_name='weekly_status', on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField(default=get_current_year)
    week = models.PositiveSmallIntegerField(default=get_current_week)
    date = models.DateField()
    schools_total = models.PositiveIntegerField(blank=True, default=0)
    schools_connected = models.PositiveIntegerField(blank=True, default=0)

    # connectivity pie chart
    schools_connectivity_good = models.PositiveIntegerField(blank=True, default=0)
    schools_connectivity_moderate = models.PositiveIntegerField(blank=True, default=0)
    schools_connectivity_no = models.PositiveIntegerField(blank=True, default=0)
    schools_connectivity_unknown = models.PositiveIntegerField(blank=True, default=0)

    # coverage pie chart
    schools_coverage_good = models.PositiveIntegerField(blank=True, default=0)
    schools_coverage_moderate = models.PositiveIntegerField(blank=True, default=0)
    schools_coverage_no = models.PositiveIntegerField(blank=True, default=0)
    schools_coverage_unknown = models.PositiveIntegerField(blank=True, default=0)

    integration_status = models.PositiveSmallIntegerField(choices=INTEGRATION_STATUS_TYPES, default=COUNTRY_CREATED)
    avg_distance_school = models.FloatField(blank=True, default=None, null=True)
    schools_with_data_percentage = models.DecimalField(
        decimal_places=5, max_digits=6, default=0, validators=[MaxValueValidator(1), MinValueValidator(0)],
    )
    connectivity_availability = models.CharField(max_length=32, choices=CONNECTIVITY_TYPES_AVAILABILITY,
                                                 default=CONNECTIVITY_TYPES_AVAILABILITY.no_connectivity)
    coverage_availability = models.CharField(max_length=32, choices=COVERAGE_TYPES_AVAILABILITY,
                                             default=COVERAGE_TYPES_AVAILABILITY.no_coverage)

    class Meta:
        verbose_name = _('Country Summary')
        verbose_name_plural = _('Country Summary')
        ordering = ('id',)
        unique_together = ('year', 'week', 'country')

    def __str__(self):
        return f'{self.year} {self.country.name} Week {self.week} Speed - {self.connectivity_speed}'

    def save(self, **kwargs):
        self.date = Week(self.year, self.week).monday()
        super().save(**kwargs)

    @property
    def is_verified(self):
        return self.integration_status not in [self.COUNTRY_CREATED, self.SCHOOL_OSM_MAPPED]

    def update_country_status_to_joined(self):
        if self.integration_status == self.SCHOOL_OSM_MAPPED:
            self.country.schools.all().delete()
        self.integration_status = self.JOINED
        self.save(update_fields=('integration_status',))
        self.country.date_of_join = timezone.now().date()
        self.country.save(update_fields=('date_of_join',))


class SchoolWeeklyStatus(ConnectivityStatistics, TimeStampedModel, models.Model):
    # unable to use choives as should be (COVERAGE_TYPES.4g), because digit goes first
    COVERAGE_UNKNOWN = 'unknown'
    COVERAGE_NO = 'no'
    COVERAGE_2G = '2g'
    COVERAGE_3G = '3g'
    COVERAGE_4G = '4g'
    COVERAGE_TYPES = Choices(
        (COVERAGE_UNKNOWN, _('Unknown')),
        (COVERAGE_NO, _('No')),
        (COVERAGE_2G, _('2G')),
        (COVERAGE_3G, _('3G')),
        (COVERAGE_4G, _('4G')),
    )

    school = models.ForeignKey(School, related_name='weekly_status', on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField(default=get_current_year)
    week = models.PositiveSmallIntegerField(default=get_current_week)
    date = models.DateField()
    num_students = models.PositiveSmallIntegerField(blank=True, default=None, null=True)
    num_teachers = models.PositiveSmallIntegerField(blank=True, default=None, null=True)
    num_classroom = models.PositiveSmallIntegerField(blank=True, default=None, null=True)
    num_latrines = models.PositiveSmallIntegerField(blank=True, default=None, null=True)
    running_water = models.BooleanField(default=False)
    electricity_availability = models.BooleanField(default=False)
    computer_lab = models.BooleanField(default=False)
    num_computers = models.PositiveSmallIntegerField(blank=True, default=None, null=True)
    connectivity = models.NullBooleanField(default=None)
    connectivity_type = models.CharField(_('Type of internet connection'), max_length=64, default='unknown')
    coverage_availability = models.NullBooleanField(default=None)
    coverage_type = models.CharField(max_length=8, default=COVERAGE_TYPES.unknown,
                                     choices=COVERAGE_TYPES)

    class Meta:
        verbose_name = _('School Summary')
        verbose_name_plural = _('School Summary')
        ordering = ('id',)
        unique_together = ('year', 'week', 'school')

    def __str__(self):
        return f'{self.year} {self.school.name} Week {self.week} Speed - {self.connectivity_speed}'

    def save(self, **kwargs):
        self.date = self.get_date()
        super().save(**kwargs)

    def get_date(self):
        return Week(self.year, self.week).monday()

    def get_connectivity_status(self, availability):
        if availability in [CountryWeeklyStatus.CONNECTIVITY_TYPES_AVAILABILITY.static_speed,
                            CountryWeeklyStatus.CONNECTIVITY_TYPES_AVAILABILITY.realtime_speed]:
            return statuses_schema.get_connectivity_status_by_connectivity_speed(self.connectivity_speed)

        elif availability == CountryWeeklyStatus.CONNECTIVITY_TYPES_AVAILABILITY.connectivity:
            return statuses_schema.get_status_by_availability(self.connectivity)

    def get_coverage_status(self, availability):
        if availability == CountryWeeklyStatus.COVERAGE_TYPES_AVAILABILITY.coverage_type:
            return statuses_schema.get_coverage_status_by_coverage_type(self.coverage_type)

        elif availability == CountryWeeklyStatus.COVERAGE_TYPES_AVAILABILITY.coverage_availability:
            return statuses_schema.get_status_by_availability(self.coverage_availability)


class CountryDailyStatus(ConnectivityStatistics, TimeStampedModel, models.Model):
    country = models.ForeignKey(Country, related_name='daily_status', on_delete=models.CASCADE)
    date = models.DateField()

    class Meta:
        verbose_name = _('Country Daily Connectivity Summary')
        verbose_name_plural = _('Country Daily Connectivity Summary')
        ordering = ('id',)
        unique_together = ('date', 'country')

    def __str__(self):
        year, week, weekday = self.date.isocalendar()
        return f'{year} {self.country.name} Week {week} Day {weekday} Speed - {self.connectivity_speed}'


class SchoolDailyStatus(ConnectivityStatistics, TimeStampedModel, models.Model):
    school = models.ForeignKey(School, related_name='daily_status', on_delete=models.CASCADE)
    date = models.DateField()

    objects = ApproxQuerySet.as_manager()

    class Meta:
        verbose_name = _('School Daily Connectivity Summary')
        verbose_name_plural = _('School Daily Connectivity Summary')
        ordering = ('id',)
        unique_together = ('date', 'school')

    def __str__(self):
        year, week, weekday = self.date.isocalendar()
        return f'{year} {self.school.name} Week {week} Day {weekday} Speed - {self.connectivity_speed}'


class RealTimeConnectivity(ConnectivityStatistics, TimeStampedModel, models.Model):
    school = models.ForeignKey(School, related_name='realtime_status', on_delete=models.CASCADE)

    objects = ApproxQuerySet.as_manager()

    class Meta:
        verbose_name = _('Real Time Connectivity Data')
        verbose_name_plural = _('Real Time Connectivity Data')
        ordering = ('id',)

    def __str__(self):
        return f'{self.created} {self.school.name} Speed - {self.connectivity_speed}'
