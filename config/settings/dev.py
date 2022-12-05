from django.core.exceptions import ImproperlyConfigured

from config.settings.base import *  # noqa: F403

DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

SECRET_KEY = env('SECRET_KEY', default='test_key')

ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ['127.0.0.1']

ADMINS = (
    ('Dev Email', env('DEV_ADMIN_EMAIL', default='admin@localhost')),
)
MANAGERS = ADMINS


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
# --------------------------------------------------------------------------

DATABASES = {
    'default': env.db(default='postgis://localhost/proco'),
}

try:
    DATABASES['realtime'] = env.db_url(var='REALTIME_DATABASE_URL')
    DATABASES['dailycheckapp_realtime'] = env.db_url(var='REALTIME_DAILYCHECKAPP_DATABASE_URL')
except ImproperlyConfigured:
    DATABASES['realtime'] = DATABASES['default']
    DATABASES['dailycheckapp_realtime'] = DATABASES['default']


# Email settings
# --------------------------------------------------------------------------

DEFAULT_FROM_EMAIL = 'noreply@example.com'
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

if CELERY_ENABLED:
    MAILING_USE_CELERY = False


# Debug toolbar installation
# --------------------------------------------------------------------------

INSTALLED_APPS += (
    'debug_toolbar',
)

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
INTERNAL_IPS = ('127.0.0.1',)


if CELERY_ENABLED:
    # Celery configurations
    # http://docs.celeryproject.org/en/latest/configuration.html
    # --------------------------------------------------------------------------

    CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='amqp://guest@localhost//')

    CELERY_TASK_ALWAYS_EAGER = True


# Sentry config
# -------------

SENTRY_ENABLED = False


# Mapbox
# --------------

MAPBOX_KEY = env('MAPBOX_KEY', default='')
