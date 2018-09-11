from .base import *

DEBUG = True

INSTALLED_APPS = [
    'silk',
]

MIDDLEWARE += [
    'silk.middleware.SilkyMiddleware',
]

"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'student_database',
        'USER': 'student_user',
        'PASSWORD': '123qweasd',
        'HOST': 'localhost',
        'PORT': '',
    }
}
"""
