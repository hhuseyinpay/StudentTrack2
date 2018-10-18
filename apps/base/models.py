from django.db import models


# Create your models here.

class Course(models.Model):
    name = models.TextField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ('name',)  # django admin için

    def __str__(self):
        return str(self.name)


class Groups(models.Model):
    name = models.TextField()
    description = models.TextField(blank=True)

    courses = models.ManyToManyField(Course, related_name="group_course")

    def __str__(self):
        return self.name
