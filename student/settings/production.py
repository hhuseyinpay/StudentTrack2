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
        'CONN_MAX_AGE': 60 * 10,  # 10 minutes
    }
}
