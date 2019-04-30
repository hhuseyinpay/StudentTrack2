from django.apps import AppConfig
from simple_history.signals import pre_create_historical_record

from student.utils.signals import add_history_ip_address


class UtilsConfig(AppConfig):
    name = 'student.utils'
    label = 'utils'
    verbose_name = 'Utils'

    def ready(self):
        from student.account.models import User

        pre_create_historical_record.connect(
            receiver=add_history_ip_address,
            sender=User,
            dispatch_uid="my_unique_identifier"
        )
