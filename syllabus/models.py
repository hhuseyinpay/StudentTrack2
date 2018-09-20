from django.db import models
from django.conf import settings

from base.models import Course


# Create your models here.

class SyllabusManager(models.Manager):
    def level(self, level):
        return Syllabus.objects.filter(level=level)

    def level_course(self, level, course):
        return Syllabus.objects.filter(level=level, course=course)


class Syllabus(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    level = models.SmallIntegerField()

    class Meta:
        unique_together = (('course', 'level'),)
        ordering = ('course', 'level')  # django admin için

    objects = SyllabusManager()

    def __str__(self):
        return str(self.course.name) + " | " + str(self.level)


class Content(models.Model):
    name = models.TextField()
    description = models.TextField(blank=True)

    week = models.SmallIntegerField()
    syllabus = models.ForeignKey(Syllabus, related_name="contents", on_delete=models.CASCADE)

    class Meta:
        unique_together = (('week', 'syllabus'),)
        ordering = ('syllabus', 'week', 'name')  # django admin için

    # amount = models.FloatField()

    def __str__(self):
        return str(self.syllabus) + " >> " + str(self.week) + " | " + str(self.name)


class UserSyllabusManager(models.Manager):
    def user(self, user):
        return UserSyllabus.objects.filter(user=user)


class UserSyllabus(models.Model):
    class Meta:
        unique_together = (('content', 'user'),)

    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    is_validated = models.BooleanField(default=False)
    validator_user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='syllabus_validator_user',
                                          on_delete=models.CASCADE, blank=True, null=True)

    objects = UserSyllabusManager()
