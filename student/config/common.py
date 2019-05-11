import os
from os.path import join
from celery.schedules import crontab

import dj_database_url
from configurations import Configuration
from corsheaders.defaults import default_headers

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Common(Configuration):
    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',

        # Third party apps
        'rest_framework',  # utilities for rest apis
        'rest_framework.authtoken',  # token authentication
        'django_filters',  # for filtering rest endpoints
        'drf_yasg',  # swagger
        'corsheaders',  # for ajax queries
        'django_celery_beat',
        'cachalot',
        'simple_history',

        # Your apps
        'student.account',
        'student.course',
        'student.location',
        'student.syllabus',
        'student.daily_study',
        'student.report',
        'student.utils',
    )

    # https://docs.djangoproject.com/en/2.0/topics/http/middleware/
    MIDDLEWARE = (
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        # 'corsheaders.middleware.CorsMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',

        'simple_history.middleware.HistoryRequestMiddleware',
    )

    ALLOWED_HOSTS = ["*"]
    ROOT_URLCONF = 'student.urls'
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'test')
    WSGI_APPLICATION = 'student.wsgi.application'

    # Email
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

    ADMINS = (
        ('Author', 'hhuseyinpay@gmail.com'),
    )

    # Postgres
    DATABASES = {
        'default': dj_database_url.config(
            default='postgres://' + os.environ.get('POSTGRES_USER') + ':' + os.environ.get(
                'POSTGRES_PASSWORD') + '@postgres:5432/' + os.environ.get('POSTGRES_DB'),
            conn_max_age=999999#conn_max_age=int(os.environ.get('POSTGRES_CONN_MAX_AGE', 600))
        )
    }

    # General
    APPEND_SLASH = False
    TIME_ZONE = 'Europe/Istanbul'
    LANGUAGE_CODE = 'tr-TR'
    # If you set this to False, Django will make some optimizations so as not
    # to load the internationalization machinery.
    USE_I18N = False
    USE_L10N = True
    USE_TZ = True
    LOGIN_REDIRECT_URL = '/'

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.0/howto/static-files/
    STATIC_ROOT = os.path.normpath(join(os.path.dirname(BASE_DIR), 'static'))
    STATICFILES_DIRS = []
    STATIC_URL = '/static/'
    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )

    # Media files
    MEDIA_ROOT = join(os.path.dirname(BASE_DIR), 'media')
    MEDIA_URL = '/media/'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': STATICFILES_DIRS,
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

    # Set DEBUG to False as a default for safety
    # https://docs.djangoproject.com/en/dev/ref/settings/#debug
    DEBUG = os.environ.get('DJANGO_DEBUG', 'False')

    # Password Validation
    # https://docs.djangoproject.com/en/2.0/topics/auth/passwords/#module-django.contrib.auth.password_validation
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

    # Logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'django.server': {
                '()': 'django.utils.log.ServerFormatter',
                'format': '[%(server_time)s] %(message)s',
            },
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        'handlers': {
            'django.server': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'django.server',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler'
            }
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'propagate': True,
            },
            'django.server': {
                'handlers': ['django.server'],
                'level': 'INFO',
                'propagate': False,
            },
            'django.request': {
                'handlers': ['mail_admins', 'console'],
                'level': 'ERROR',
                'propagate': False,
            },
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'INFO'
            },
        }
    }

    # Custom user app
    AUTH_USER_MODEL = 'account.User'

    # Django Rest Framework
    REST_FRAMEWORK = {
        # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        # 'PAGE_SIZE': int(os.getenv('DJANGO_PAGINATION_LIMIT', 10)),

        'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S%z',
        'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
        ),
        'DEFAULT_PARSER_CLASSES': (
            'rest_framework.parsers.JSONParser',
        ),
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.SessionAuthentication',
            'rest_framework.authentication.TokenAuthentication',
            'rest_framework.authentication.BasicAuthentication',
        ),
        'DEFAULT_FILTER_BACKENDS': (
            'django_filters.rest_framework.DjangoFilterBackend',
            'rest_framework.filters.OrderingFilter'
        ),
        'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning'
    }

    CORS_ORIGIN_ALLOW_ALL = True
    CORS_ALLOW_HEADERS = default_headers + ('x-token',)

    # CELERY
    CELERY_BROKER_URL = 'redis://redis:6379/'
    CELERY_RESULT_BACKEND = 'redis://redis:6379/'
    CELERY_ACCEPT_CONTENT = ['application/json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'Europe/Istanbul'

    CELERY_BEAT_SCHEDULE = {
        'fill-today-daily-study': {
            'task': 'student.daily_study.tasks.fill_today_daily_study',
            'schedule': crontab(minute=0, hour=00)
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