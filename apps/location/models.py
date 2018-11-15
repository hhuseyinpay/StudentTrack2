from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()


class Region(models.Model):
    name = models.TextField(unique=True)
    description = models.TextField(blank=True)

    admins = models.ManyToManyField(User, related_name='region_admin', blank=True)

    def __str__(self):
        return self.name


class Area(models.Model):
    name = models.TextField(unique=True)
    description = models.TextField(blank=True)

    executives = models.ManyToManyField(User, related_name='area_executive', blank=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ClassRoom(models.Model):
    name = models.TextField()
    description = models.TextField(blank=True)

    teachers = models.ManyToManyField(User, related_name='classroom_teacher', blank=True)
    area = models.ForeignKey(Area, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name
