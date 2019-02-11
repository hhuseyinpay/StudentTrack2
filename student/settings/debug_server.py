from .base import *

DEBUG = True

INSTALLED_APPS += [
    'silk',
]

MIDDLEWARE += [
    'silk.middleware.SilkyMiddleware',
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tts',
        'USER': 'power_user',
        'PASSWORD': '1',
        'HOST': 'localhost',
        'PORT': '',
    }
}

