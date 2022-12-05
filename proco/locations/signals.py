from django.db.models.signals import post_save
from django.dispatch import receiver

from proco.connection_statistics.models import CountryWeeklyStatus
from proco.locations.models import Country


@receiver(post_save, sender=Country)
def create_country_weekly_status(instance, created=False, **kwargs):
    if created:
        CountryWeeklyStatus.objects.create(country=instance)


@receiver(post_save, sender=CountryWeeklyStatus)
def set_date_of_join(instance, created=False, **kwargs):
    if created:
        country = instance.country
        country_last_status = CountryWeeklyStatus.objects.filter(pk=country.last_weekly_status_id).first()

        if not country_last_status or country_last_status.date < instance.date:
            country.last_weekly_status = instance
            country.save()
