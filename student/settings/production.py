from .base import *

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
        'HOST': 'localhost',
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
