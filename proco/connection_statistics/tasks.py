from datetime import timedelta

from django.utils import timezone

from celery import chain, chord, group

from proco.connection_statistics.models import RealTimeConnectivity
from proco.connection_statistics.utils import (
    aggregate_real_time_data_to_school_daily_status,
    aggregate_school_daily_status_to_school_weekly_status,
    aggregate_school_daily_to_country_daily,
    update_country_weekly_status,
)
from proco.locations.models import Country
from proco.realtime_unicef.utils import sync_realtime_data
from proco.realtime_dailycheckapp.utils import sync_dailycheckapp_realtime_data
from proco.schools.loaders.brasil_loader import brasil_statistic_loader
from proco.taskapp import app


@app.task(soft_time_limit=4 * 60 * 60, time_limit=4 * 60 * 60)
def aggregate_country_data(_prev_result, country_id, *args):
    date = timezone.now().date()
    country = Country.objects.get(id=country_id)

    aggregate_real_time_data_to_school_daily_status(country, date)
    aggregate_school_daily_to_country_daily(country, date)
    weekly_data_available = aggregate_school_daily_status_to_school_weekly_status(country)
    if weekly_data_available:
        update_country_weekly_status(country)

    country.invalidate_country_related_cache()


@app.task(soft_time_limit=60 * 60, time_limit=60 * 60)
def finalize_daily_data(_prev_result, country_id, *args):
    date = timezone.now().date() - timedelta(days=1)
    country = Country.objects.get(id=country_id)

    aggregate_real_time_data_to_school_daily_status(country, date)
    aggregate_school_daily_to_country_daily(country, date)
    # todo: ideally data should be aggregated on monday for all previous week,
    #  but it require a lot of work to re-write weekly aggregates, so only sunday daily data will be updated for now


@app.task(soft_time_limit=4 * 60 * 60, time_limit=4 * 60 * 60)
def update_brasil_schools():
    brasil_statistic_loader.update_schools()
    brasil_statistic_loader.country.invalidate_country_related_cache()


@app.task(soft_time_limit=30 * 60, time_limit=30 * 60)
def load_brasil_daily_statistics(*args):
    brasil_statistic_loader.update_statistic()


@app.task(soft_time_limit=60 * 60, time_limit=60 * 60)
def load_data_from_unicef_db(*args):
    sync_realtime_data()

@app.task(soft_time_limit=60 * 60, time_limit=60 * 60)
def load_data_from_dailycheckapp_db(*args):
    sync_dailycheckapp_realtime_data()


@app.task
def finalize_task():
    return 'Done'


@app.task
def update_real_time_data(today=True):
    countries_ids = Country.objects.values_list('id', flat=True)

    if today:
        date = timezone.now().date()
        aggregate_task = aggregate_country_data
    else:
        date = timezone.now().date() - timedelta(days=1)
        aggregate_task = finalize_daily_data

    chain(
        load_data_from_dailycheckapp_db.s(),       
        load_data_from_unicef_db.s(),        
        load_brasil_daily_statistics.s(),
        chord(
            group([
                aggregate_task.s(country_id, date)
                for country_id in countries_ids
            ]),
            finalize_task.si(),
        ), 
       
    ).delay()


@app.task
def clean_old_realtime_data():
    RealTimeConnectivity.objects.filter(created__lt=timezone.now() - timedelta(days=30)).delete()
