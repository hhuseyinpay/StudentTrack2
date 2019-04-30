from django.db import models
from django.utils.timezone import now

from student.account.models import User
from student.course.models import Course


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
        return str(self.id) + ' | ' + str(self.user.classroom) + ' - ' \
               + str(self.user) + ' | ' + self._str_updated()

    def _str_updated(self):
        if self.updated is None:
            return "***"
        else:
            return str(self.updated.date())


class Study(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, db_index=False)
    daily_study = models.ForeignKey(DailyStudy, related_name='studies', on_delete=models.CASCADE)

    begining = models.FloatField()
    end = models.FloatField()
    amount = models.FloatField()

    class Meta:
        ordering = ('-course__importance',)  # django admin için

    def __str__(self):
        return str(self.id) + ' | ' + str(self.course.name)
