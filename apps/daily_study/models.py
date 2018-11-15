from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now

from course.models import Course

# Create your models here.
User = get_user_model()


class DailyStudy(models.Model):
    created_day = models.DateField(default=now, db_index=True)
    timestamp = models.DateTimeField(default=now)
    updated = models.DateTimeField(blank=True, null=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # onaylayan kişi
    is_validated = models.BooleanField(default=False)
    validate_time = models.DateTimeField(blank=True, null=True)
    validator_user = models.ForeignKey(User, related_name="dailystudy_validator_user",
                                       on_delete=models.SET_NULL, blank=True, null=True, db_index=False)

    def __str__(self):
        return str(self.id) + ' | ' + str(self.user)


class Study(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, db_index=False)
    daily_study = models.ForeignKey(DailyStudy, related_name='studies', on_delete=models.CASCADE)

    begining = models.FloatField()
    end = models.FloatField()
    amount = models.FloatField()

    def __str__(self):
        return str(self.id) + ' | ' + str(self.course.name)
