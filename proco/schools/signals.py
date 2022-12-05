from datetime import datetime

from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from proco.connection_statistics.models import CountryWeeklyStatus, SchoolWeeklyStatus
from proco.schools.models import School


@receiver(post_save, sender=School)
def change_integration_status_country(instance, created=False, **kwargs):
    if created or instance.geopoint:
        country_weekly = CountryWeeklyStatus.objects.filter(country_id=instance.country.id).last()
        country_weekly_exists = bool(country_weekly)
        year, week, weekday = timezone.now().isocalendar()
        if not (country_weekly.year == year and country_weekly.week == week):
            country_weekly.id = None
            country_weekly.year = year
            country_weekly.week = week
            country_weekly.save()

        if instance.geopoint:
            if country_weekly.integration_status == CountryWeeklyStatus.JOINED:
                country_weekly.integration_status = CountryWeeklyStatus.SCHOOL_MAPPED
                instance.country.date_schools_mapped = datetime.strptime(
                    f'{country_weekly.year}-W{country_weekly.week}-1', '%Y-W%W-%w')
                instance.country.save(update_fields=('date_schools_mapped',))
                if country_weekly.id:
                    country_weekly.save(update_fields=('integration_status',))
                else:
                    country_weekly.save()

        if created:
            if country_weekly_exists:
                country_weekly.schools_total = F('schools_total') + 1
                country_weekly.schools_connectivity_unknown = F('schools_connectivity_unknown') + 1
                country_weekly.save(update_fields=('schools_total', 'schools_connectivity_unknown'))
            else:
                country_weekly.schools_connectivity_unknown = 1
                country_weekly.schools_total = 1
                country_weekly.save()


@receiver(post_save, sender=SchoolWeeklyStatus)
def update_school_last_weekly_status(instance, created=False, **kwargs):
    school = instance.school
    school_last_status = school.last_weekly_status
    if not school_last_status:
        school.last_weekly_status = instance
        school.save()
    elif school_last_status.date < instance.date:
        school.last_weekly_status = instance
        school.save()
