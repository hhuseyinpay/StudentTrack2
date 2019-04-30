from django.db import models
from django.contrib.auth import get_user_model
from model_utils.models import TimeStampedModel
# Create your models here.
from student.account.models import User


class Region(TimeStampedModel):
    name = models.TextField(unique=True)
    description = models.TextField(blank=True)

    admins = models.ManyToManyField(User, related_name='region_admin', blank=True)

    def __str__(self):
        return self.name


class Area(TimeStampedModel):
    name = models.TextField()
    description = models.TextField(blank=True)

    executives = models.ManyToManyField(User, related_name='area_executive', blank=True)
    region = models.ForeignKey(Region, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.region.name + ' | ' + self.name


class ClassRoom(TimeStampedModel):
    name = models.TextField()
    description = models.TextField(blank=True)

    teachers = models.ManyToManyField(User, related_name='classroom_teacher', blank=True)
    area = models.ForeignKey(Area, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.area.region.name + ' | ' + self.area.name + ' | ' + self.name
