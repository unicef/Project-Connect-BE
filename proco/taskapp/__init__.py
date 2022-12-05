import os

from django.conf import settings

from celery import Celery
from celery.schedules import crontab

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

app = Celery('proco')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.timezone = 'UTC'


@app.on_after_finalize.connect
def finalize_setup(sender, **kwargs):
    from drf_secure_token.tasks import DELETE_OLD_TOKENS

    app.conf.beat_schedule.update({
        'proco.connection_statistics.tasks.aggregate_today_data': {
            'task': 'proco.connection_statistics.tasks.update_real_time_data',
            'schedule': crontab(hour='4,10,16,20', minute=0),
            'args': (),
            'kwargs': {'today': True},
        },
        'proco.connection_statistics.tasks.aggregate_yesterday_data': {
            'task': 'proco.connection_statistics.tasks.update_real_time_data',
            'schedule': crontab(hour=0, minute=1),
            'args': (),
            'kwargs': {'today': False},
        },
        'proco.connection_statistics.tasks.update_brasil_schools': {
            'task': 'proco.connection_statistics.tasks.update_brasil_schools',
            'schedule': crontab(hour=1, minute=0),
            'args': (),
        },
        'proco.utils.tasks.update_all_cached_values': {
            'task': 'proco.utils.tasks.update_all_cached_values',
            'schedule': crontab(hour=3, minute=0),
            'args': (),
        },
        'proco.connection_statistics.tasks.clean_old_realtime_data': {
            'task': 'proco.connection_statistics.tasks.clean_old_realtime_data',
            'schedule': crontab(hour=5, minute=0),
            'args': (),
        },
        'drf_secure_token.tasks.delete_old_tokens': DELETE_OLD_TOKENS,
    })
