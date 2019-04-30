from django.db import models


# Create your models here.

class Course(models.Model):
    name = models.TextField()
    description = models.TextField(blank=True)
    importance = models.IntegerField(default=0)

    class Meta:
        ordering = ('-importance',)  # django admin için

    def __str__(self):
        return str(self.name)


class CourseGroups(models.Model):
    name = models.TextField()
    description = models.TextField(blank=True)

    courses = models.ManyToManyField(Course, related_name="groups")

    def __str__(self):
        return self.name
