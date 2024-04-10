"""
Django settings for authors project.

Generated by 'django-admin startproject' using Django 1.11.14.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
# import django_heroku

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    '7pgozr2jn7zs_o%i8id6=rddie!*0f0qy3$oy$(8231i^4*@u3'),

DEBUG = os.environ.get('DEBUG', 'True'),

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.herokuapp.com', '.3.us-1.fl0.io']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'django_extensions',
    'rest_framework',
    'rest_framework_swagger',
    'authors.apps.authentication',
    'authors.apps.core',
    'authors.apps.profiles',
    'drf_yasg',
    'authors.apps.articles',
    'django_filters',
    'authors.apps.notification'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'authors.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'authors.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', 'authors_prime'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'TIME_ZONE':'UTC'
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

CORS_ORIGIN_ALLOW_ALL = True

AUTH_USER_MODEL = 'authentication.User'

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'authors.apps.core.exceptions.core_exception_handler',
    'NON_FIELD_ERRORS_KEY': 'error',

    'DEfULT_AUTHENTICATION_CLASSES': (
        'authors.apps.authentication.backends.JWTAuthentication',
    ),

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,

    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    )
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    },
}

# django_heroku.settings(locals())

EMAIL_USE_TLS = True
EMAIL_HOST = os.environ.get('EMAIL_HOST', )
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', )
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', )
EMAIL_PORT = 587
TWITTER_CONSUMER_API_KEY = os.environ.get('TWITTER_CONSUMER_API_KEY')
TWITTER_CONSUMER_API_SECRET = os.environ.get('TWITTER_CONSUMER_API_SECRET')
SOCIAL_PASSWORD = os.environ.get('SOCIAL_PASSWORD')

# Article reading time configurations
# Number of words proccesed by an average adult in a minute
WORD_PER_MINUTE = 265
# Each word is standardized to be five characters long.
WORD_LENGTH = 5

# django_heroku.settings(locals())
