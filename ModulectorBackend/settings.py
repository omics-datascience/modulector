"""
Django settings for ModulectorBackend project.

Generated by 'django-admin startproject' using Django 3.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Modulector version
VERSION: str = '2.2.1'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'm)95!xjla3k1h)1#ya_rp^7#7^l_laaa6x$ik2_vx#gc0ll=e('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['web', 'localhost', '127.0.0.1', '::1']

# Modulector unsubscribe endpoint
UNSUBSCRIBE_URL = 'http://localhost:8000/unsubscribe-pubmeds/?token='
DEFAULT_FROM_EMAIL = 'multiomix@gmail.com'
NCBI_API_KEY = '61a2e5671d5d57b8dde8a61cad17eec99709'
# to enable and disable api call to pubmeds in the mirna interactions and mirna target interactions endpoints
USE_PUBMED_API = True
PUBMED_API_TIMEOUT = 1
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django_crontab',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'modulector.apps.ModulectorConfig',
    'rest_framework',
    'django_filters',
    'django_generate_secret_key',
    'drf_spectacular',
    'drf_spectacular_sidecar'
]

CRONJOBS = [
    ('0 0 * * SAT', 'modulector.pubmed_job.execute',
     '>> ' + BASE_DIR + '/jobs_log.log')
]
CRONTAB_LOCK_JOBS = True
ALLOW_PARALLEL_RUNS = False
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    # 'DEFAULT_PERMISSION_CLASSES': (
    #  'rest_framework.permissions.DjangoModelPermissions',
    # )
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': []
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Modulector',
    'DESCRIPTION': """
### An open platform which provides information about methylation sites, miRNAs and genes from different popular databases.  
The platform is part of the Multiomix project. For more information, visit our [website](https://omicsdatascience.org/).
To contribute: [OmicsDatascience](https://github.com/omics-datascience/modulector)""",
    'VERSION': VERSION,
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_DIST': 'SIDECAR', 
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    'SCHEMA_PATH_PREFIX': '/api/',
    'SWAGGER_UI_SETTINGS': {
            'defaultModelsExpandDepth': -1, 
            'displayRequestDuration': False,
            'docExpansion': 'none',
            'filter': False,
            'showExtensions': True,
            'showCommonExtensions': True,
    }
}


ROOT_URLCONF = 'ModulectorBackend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ModulectorBackend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': os.getenv('POSTGRES_USERNAME', 'modulector'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'modulector'),
        'HOST': os.getenv('POSTGRES_HOST', '127.0.0.1'),
        'PORT': os.getenv('POSTGRES_PORT', 5432),
        'NAME': os.getenv('POSTGRES_DB', 'modulector'),
    },
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# According to documentation (https://docs.djangoproject.com/en/4.2/ref/databases/#connection-management)
# this is more robust than the default
CONN_HEALTH_CHECKS = True

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

# Media files
MEDIA_ROOT = os.getenv('MEDIA_ROOT', os.path.join(BASE_DIR, ''))
MEDIA_URL = os.getenv('MEDIA_URL', '/media/')

# Test runner
TEST_RUNNER = 'modulector.tests.runner.DjangoTestSuiteRunner'

# Email Server
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# This email configuration is what postfix uses, for production, use your own
EMAIL_HOST = 'localhost'
EMAIL_PORT = '25'
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False

# Number of processes in the ProcessPoolExecutor
PROCESS_POOL_WORKERS: int = int(os.getenv('PROCESS_POOL_WORKERS', 4))
