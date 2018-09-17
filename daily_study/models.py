from datetime import datetime, timedelta, date

from django.db import models
from django.conf import settings
from django.utils.timezone import now
from base.models import Course


# Create your models here.


class DailyStudyManager(models.Manager):
    def get_by_interval(self, user, begining, end):
        try:
            datetime.strptime(begining, '%Y-%m-%d')
            datetime.strptime(end, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        return DailyStudy.objects.filter(user=user, created_day__gte=begining, created_day__lte=end).order_by(
            "-timestamp")

    def get_day(self, user):
        x = date.today() - timedelta(days=7)
        return DailyStudy.objects.filter(user=user, created_day=x).order_by("-timestamp")

    def user_editables(self, user):
        # is_validated false ve aynı gün içinde olunca editlenebilir.
        today = date.today()
        return DailyStudy.objects.filter(created_day=today, user=user, is_validated=False)


class DailyStudy(models.Model):
    created_day = models.DateField(default=now, db_index=True)
    timestamp = models.DateTimeField(default=now)
    updated = models.DateTimeField(blank=True, null=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # onaylayan kişi
    is_validated = models.BooleanField(default=False)
    validate_time = models.DateTimeField(blank=True, null=True)
    validator_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="dailystudy_validator_user",
                                       on_delete=models.CASCADE, blank=True, null=True)

    objects = DailyStudyManager()

    def __str__(self):
        return str(self.id) + ' | ' + str(self.user)


class Study(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    studies = models.ForeignKey(DailyStudy, related_name='studies', on_delete=models.CASCADE)

    begining = models.FloatField()
    end = models.FloatField()
    amount = models.FloatField()

    def __str__(self):
        return str(self.id) + ' | ' + str(self.course.name)
