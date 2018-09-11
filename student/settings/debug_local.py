from .base import *

DEBUG = True

INSTALLED_APPS += [
    'silk',
    'django_extensions',
]

MIDDLEWARE += [
    'silk.middleware.SilkyMiddleware',
]

# postgre için
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    }
}
"""
