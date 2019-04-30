import os
import sentry_sdk

from .common import Common


class Production(Common):
    INSTALLED_APPS = Common.INSTALLED_APPS
    DEBUG = False
    # Site
    # https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts
    ALLOWED_HOSTS = ["*"]
    INSTALLED_APPS += ("gunicorn",)

    @classmethod
    def post_setup(cls):
        from sentry_sdk.integrations.django import DjangoIntegration
        sentry_sdk.init(
            dsn="https://b814830e5c9f426dbf4b572a2edc3325@sentry.io/1449657",
            integrations=[DjangoIntegration()]
        )
