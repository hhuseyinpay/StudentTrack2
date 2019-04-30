from django.utils.translation import ugettext_lazy as _
from django.db import models

from simple_history.models import HistoricalRecords


class IPAddressHistoricalModel(models.Model):
    """
    Abstract model for history models tracking the IP address.
    """
    ip_address = models.GenericIPAddressField(_('IP address'))

    class Meta:
        abstract = True


class StudentBaseModel(models.Model):
    history = HistoricalRecords(inherit=True)  # (bases=[IPAddressHistoricalModel, ], inherit=True)

    class Meta:
        abstract = True


class StudentBaseManager(models.Manager):
    pass
