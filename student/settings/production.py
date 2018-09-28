from .base import *

DEBUG = False

# INSTALLED_APPS += []

# MIDDLEWARE += []


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tts',
        'USER': 'tts-db-user',
        'PASSWORD': '1',
        'HOST': 'localhost',
        'PORT': '',
    }
}

