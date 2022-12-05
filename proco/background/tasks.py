from typing import List

from django.utils import timezone

from celery import current_task

from proco.background.models import BackgroundTask
from proco.locations.models import Country
from proco.taskapp import app


@app.task(soft_time_limit=30 * 60, time_limit=30 * 60)
def reset_countries_data(ids: List):
    task = BackgroundTask.objects.get_or_create(task_id=current_task.request.id)[0]

    queryset = Country.objects.filter(id__in=ids)
    task.info(f'{", ".join(map(str, queryset))} reset started')

    for obj in queryset:
        task.info(f'{obj} started')
        obj._clear_data_country()
        obj.invalidate_country_related_cache()
        task.info(f'{obj} completed')

    task.status = BackgroundTask.STATUSES.completed
    task.completed_at = timezone.now()
    task.save()


@app.task(soft_time_limit=30 * 60, time_limit=30 * 60)
def validate_countries(ids: List):
    task = BackgroundTask.objects.get_or_create(task_id=current_task.request.id)[0]

    queryset = Country.objects.filter(id__in=ids)
    task.info(f'{", ".join(map(str, queryset))} validation started')

    for obj in queryset:
        task.info(f'{obj} started')
        if not obj.last_weekly_status.is_verified:
            obj.last_weekly_status.update_country_status_to_joined()
            obj.invalidate_country_related_cache()
            task.info(f'{obj} completed')
        else:
            task.info(f'{obj} already verified')

    task.status = BackgroundTask.STATUSES.completed
    task.completed_at = timezone.now()
    task.save()
