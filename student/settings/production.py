from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://086dec006bf6402587d9e5e7ac7b4af6@sentry.io/1324498",
    integrations=[DjangoIntegration()]
)
DEBUG = False

INSTALLED_APPS += [

    'cachalot',
]

# MIDDLEWARE += []


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tts',
        'USER': 'tts-db-user',
        'PASSWORD': '1',
        'HOST': 'db',
        'PORT': '',
        'CONN_MAX_AGE': 60 * 10,  # 10 minutes
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
