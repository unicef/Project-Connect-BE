import sentry_sdk
from kombu import Exchange, Queue  # NOQA
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from config.settings.base import *  # noqa: F403
from config.utils import get_git_hash

environ.Env.read_env()


DEBUG = False

ADMINS = env.json('ADMINS')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

SECRET_KEY = env('SECRET_KEY')


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
# --------------------------------------------------------------------------

DATABASES = {
    'default': env.db(),
    'realtime': env.db_url(var='REALTIME_DATABASE_URL'),
    'dailycheckapp_realtime': env.db_url(var='REALTIME_DAILYCHECKAPP_DATABASE_URL'),
}


# Template
# --------------------------------------------------------------------------

TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]


# --------------------------------------------------------------------------

USE_COMPRESSOR = env.bool('USE_COMPRESSOR')
USE_CLOUDFRONT = env.bool('USE_CLOUDFRONT')
USE_HTTPS = env.bool('USE_HTTPS')
if USE_HTTPS:
    LETSENCRYPT_DIR = env('LETSENCRYPT_DIR', default='/opt/letsencrypt/')


# Storage configurations
# --------------------------------------------------------------------------

AZURE_ACCOUNT_NAME = env('AZURE_ACCOUNT_NAME')  # noqa: F405
AZURE_ACCOUNT_KEY = env('AZURE_ACCOUNT_KEY')  # noqa: F405
AZURE_CONTAINER = env('AZURE_CONTAINER')  # noqa: F405
AZURE_SSL = True
AZURE_URL_EXPIRATION_SECS = None

if AZURE_ACCOUNT_NAME and AZURE_ACCOUNT_KEY and AZURE_CONTAINER:
    DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
    STATICFILES_STORAGE = 'storages.backends.azure_storage.AzureStorage'
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'


# Compressor & Cloudfront settings
# --------------------------------------------------------------------------

if USE_COMPRESSOR:
    INSTALLED_APPS += ('compressor',)
    STATICFILES_FINDERS += ('compressor.finders.CompressorFinder',)

    # See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_ENABLED
    COMPRESS_ENABLED = True

    COMPRESS_STORAGE = STATICFILES_STORAGE

    # See: http://django-compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_CSS_HASHING_METHOD
    COMPRESS_CSS_HASHING_METHOD = 'content'

    COMPRESS_CSS_FILTERS = (
        'config.settings.abs_compress.CustomCssAbsoluteFilter',
        'compressor.filters.cssmin.CSSMinFilter',
    )

    COMPRESS_OFFLINE = True
    COMPRESS_OUTPUT_DIR = 'cache'
    COMPRESS_CACHE_BACKEND = 'locmem'


# Email settings
# --------------------------------------------------------------------------

EMAIL_CONFIG = env.email()
vars().update(EMAIL_CONFIG)

SERVER_EMAIL_SIGNATURE = env('SERVER_EMAIL_SIGNATURE', default='proco'.capitalize())
DEFAULT_FROM_EMAIL = SERVER_EMAIL = SERVER_EMAIL_SIGNATURE + ' <{0}>'.format(env('SERVER_EMAIL'))


if CELERY_ENABLED:
    # Celery configurations
    # http://docs.celeryproject.org/en/latest/configuration.html
    # --------------------------------------------------------------------------

    CELERY_BROKER_URL = env('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND_URL')

    if CELERY_BROKER_URL.startswith('rediss://') or CELERY_RESULT_BACKEND.startswith('rediss://'):
        import ssl
        CELERY_REDIS_BACKEND_USE_SSL = {
            'ssl_cert_reqs': ssl.CERT_NONE,
        }

    CELERY_TASK_DEFAULT_QUEUE = 'proco-celery-queue'
    CELERY_TASK_DEFAULT_EXCHANGE = 'proco-exchange'
    CELERY_TASK_DEFAULT_ROUTING_KEY = 'celery.proco'
    CELERY_TASK_QUEUES = (
        Queue(
            CELERY_TASK_DEFAULT_QUEUE,
            Exchange(CELERY_TASK_DEFAULT_EXCHANGE),
            routing_key=CELERY_TASK_DEFAULT_ROUTING_KEY,
        ),
    )


# Sentry config
# -------------

SENTRY_DSN = env('SENTRY_DSN', default='')
SENTRY_ENABLED = True if SENTRY_DSN else False

if SENTRY_ENABLED:
    sentry_sdk.init(
        SENTRY_DSN,
        traces_sample_rate=0.2,
        release=get_git_hash(),
        integrations=[DjangoIntegration(), CeleryIntegration()],
    )


# Mapbox
# --------------

MAPBOX_KEY = env('MAPBOX_KEY', default='')
