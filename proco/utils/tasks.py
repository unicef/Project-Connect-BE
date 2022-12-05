from django.urls import reverse

from rest_framework.test import APIClient

from celery import chain

from proco.taskapp import app


@app.task(soft_time_limit=10 * 60, time_limit=11 * 60)
def update_cached_value(*args, url='', **kwargs):
    client = APIClient()
    client.get(url, {'cache': False}, format='json')


@app.task(soft_time_limit=5 * 60, time_limit=5 * 60)
def update_all_cached_values():
    from proco.locations.models import Country

    update_cached_value.delay(url=reverse('connection_statistics:global-stat'))
    update_cached_value.delay(url=reverse('locations:countries-boundary'))
    update_cached_value.delay(url=reverse('locations:countries-list'))
    update_cached_value.delay(url=reverse('schools:random-schools'))

    for country in Country.objects.all():
        chain([
            update_cached_value.s(url=reverse('locations:countries-detail', kwargs={'pk': country.code.lower()})),
            update_cached_value.s(url=reverse('schools:schools-list', kwargs={'country_code': country.code.lower()})),
        ]).delay()


@app.task
def update_country_related_cache(country_code):
    update_cached_value.delay(url=reverse('connection_statistics:global-stat'))
    update_cached_value.delay(url=reverse('locations:countries-list'))
    update_cached_value.delay(url=reverse('schools:random-schools'))
    update_cached_value.delay(url=reverse('locations:countries-detail', kwargs={'pk': country_code.lower()}))
    update_cached_value.delay(url=reverse('schools:schools-list', kwargs={'country_code': country_code.lower()}))
