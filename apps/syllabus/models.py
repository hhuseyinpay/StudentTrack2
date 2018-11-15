from django.contrib.auth import get_user_model
from django.db import models

from course.models import Course

# Create your models here.
User = get_user_model()


class SyllabusManager(models.Manager):
    def level(self, level):
        return Syllabus.objects.filter(level=level)

    def level_course(self, level, course):
        return Syllabus.objects.filter(level=level, course=course)


class Syllabus(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    level = models.SmallIntegerField()

    objects = SyllabusManager()

    class Meta:
        unique_together = (('course', 'level'),)
        ordering = ('level', 'course')  # django admin için

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

    def __str__(self):
        """
        Admin'den yeni content eklerken kolaylık sağlamak amacıyla syllabus ismini vs alıyordum
        mobil kısımda direk content name'e ihtiyaç olduğu için sadece kendi ismini döndörüyor şuanda.
        :return:
        """
        return str(self.name)  # str(self.syllabus) + " >> " + str(self.week) + " | " + str(self.name)


class UserSyllabusManager(models.Manager):
    def user(self, user):
        return UserSyllabus.objects.filter(user=user)


class UserSyllabus(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE, db_index=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    is_validated = models.BooleanField(default=False)
    validator_user = models.ForeignKey(User, related_name='syllabus_validator_user',
                                       on_delete=models.CASCADE, blank=True, null=True, db_index=False)

    objects = UserSyllabusManager()

    class Meta:
        unique_together = (('content', 'user'),)
