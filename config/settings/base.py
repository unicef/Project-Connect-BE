import environ

# Build paths inside the project like this: root(...)
env = environ.Env()

root = environ.Path(__file__) - 3
apps_root = root.path('proco')

BASE_DIR = root()

# Project name
# ------------
PROJECT_FULL_NAME = env('PROJECT_FULL_NAME', default='Project Connect')
PROJECT_SHORT_NAME = env('PROJECT_SHORT_NAME', default='Proco')

# Base configurations
# --------------------------------------------------------------------------

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

AUTH_USER_MODEL = 'custom_auth.ApplicationUser'


# Application definition
# --------------------------------------------------------------------------

DJANGO_APPS = [
    'config.apps.CustomAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.gis',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_gis',
    'drf_secure_token',
    'mptt',
    'crispy_forms',
    'mapbox_location_field',
    'corsheaders',
    'admin_reorder',
    'django_filters',
    'django_mptt_admin',
    'constance',
    'unicef_restlib',
]

LOCAL_APPS = [
    'proco.mailing',
    'proco.custom_auth',
    'proco.schools',
    'proco.locations',
    'proco.connection_statistics',
    'proco.contact',
    'proco.dailycheckapp_contact',
    'proco.background',
    'proco.realtime_unicef',
    'proco.realtime_dailycheckapp',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# Middleware configurations
# --------------------------------------------------------------------------

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'drf_secure_token.middleware.UpdateTokenMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
]


# Rest framework configuration
# http://www.django-rest-framework.org/api-guide/settings/
# --------------------------------------------------------------------------

REST_FRAMEWORK = {
    'PAGE_SIZE': 10,
    'DEFAULT_PAGINATION_CLASS': 'unicef_restlib.pagination.DynamicPageNumberPagination',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'drf_secure_token.authentication.SecureTokenAuthentication',
    ],
}


# Template configurations
# --------------------------------------------------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            root('proco', 'templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]


# Fixture configurations
# --------------------------------------------------------------------------

FIXTURE_DIRS = [
    root('proco', 'fixtures'),
]


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators
# --------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Django cache settings
# ------------------------------------

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://localhost:6379/0'),
        'TIMEOUT': 365 * 24 * 60 * 60,  # one year
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'retry_on_timeout': True,
                'socket_timeout': 5,
            },
        },
    },
}


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
# --------------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = 1


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
# --------------------------------------------------------------------------

STATIC_URL = '/static/'
STATIC_ROOT = root('static')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

STATICFILES_DIRS = [
    root('proco', 'assets'),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = root('media')


CELERY_ENABLED = env.bool('CELERY_ENABLED', default=True)
if CELERY_ENABLED:
    # Celery configuration
    # --------------------------------------------------------------------------

    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_TASK_IGNORE_RESULT = True


# Django mailing configuration
# --------------------------------------------------------------------------

if CELERY_ENABLED:
    TEMPLATED_EMAIL_BACKEND = 'proco.mailing.backends.AsyncTemplateBackend'
    MAILING_USE_CELERY = True
    

TEMPLATED_EMAIL_TEMPLATE_DIR = 'email'
TEMPLATED_EMAIL_FILE_EXTENSION = 'html'


# Images
# ---------------

IMAGES_PATH = 'images'


# Crispy forms
# ---------------

CRISPY_TEMPLATE_PACK = 'bootstrap4'


# CORS headers
# --------------

CORS_ORIGIN_ALLOW_ALL = True


# Admin Reorder Models
# --------------

ADMIN_REORDER = (
    'constance',
    {
        'app': 'custom_auth',
        'label': 'Authentication and authorization',
        'models': (
            'auth.Group',
            'custom_auth.ApplicationUser',
        ),
    },
    {
        'app': 'connection_statistics',
        'label': 'Summary',
        'models': (
            'connection_statistics.CountryWeeklyStatus',
            'connection_statistics.SchoolWeeklyStatus',
        ),
    },
    {
        'app': 'connection_statistics',
        'label': 'Real Time Connectivity Data',
        'models': (
            'connection_statistics.RealTimeConnectivity',
            'connection_statistics.CountryDailyStatus',
            'connection_statistics.SchoolDailyStatus',
        ),
    },
    'locations',
    'schools',
    'background',
    'contact',
    'dailycheckapp_contact',
)

RANDOM_SCHOOLS_DEFAULT_AMOUNT = env('RANDOM_SCHOOLS_DEFAULT_AMOUNT', default=20000)

CONTACT_MANAGERS = env.list('CONTACT_MANAGERS', default=['test@test.test'])
DAILYCHECKAPP_CONTACT_MANAGERS = env.list('DAILYCHECKAPP_CONTACT_MANAGERS', default=['test@test.test'])


CONSTANCE_REDIS_CONNECTION = env('REDIS_URL', default='redis://localhost:6379/0')
CONSTANCE_ADDITIONAL_FIELDS = {
    'email_input': ['django.forms.fields.CharField', {
        'required': False,
        'widget': 'django.forms.EmailInput',
    }],
}
CONSTANCE_CONFIG = {
    'CONTACT_EMAIL': ('', 'Email to receive contact messages', 'email_input'),
    'DAILYCHECKAPP_CONTACT_EMAIL': ('', 'Email to receive dailycheckapp_contact messages', 'email_input'),
}


# Cache control headers
CACHE_CONTROL_MAX_AGE = 24 * 60 * 60
