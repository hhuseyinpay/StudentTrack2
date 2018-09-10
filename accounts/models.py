from django.db import models
from django.contrib.auth.models import User

from base.models import Course


class Region(models.Model):
    name = models.TextField(unique=True)
    description = models.TextField(blank=True)

    admins = models.ManyToManyField(User, related_name='region_admins')

    def __str__(self):
        return self.name


class Area(models.Model):
    name = models.TextField(unique=True)
    description = models.TextField(blank=True)

    executives = models.ManyToManyField(User, related_name='area_executives')
    related_region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ClassRoom(models.Model):
    name = models.TextField()
    description = models.TextField(blank=True)

    teachers = models.ManyToManyField(User, related_name='classroom_teachers')
    related_area = models.ForeignKey(Area, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Groups(models.Model):
    name = models.TextField()
    description = models.TextField(blank=True)

    courses = models.ManyToManyField(Course, related_name="group_course")

    def __str__(self):
        return self.name


class ProfileManager(models.Manager):
    def user(self, user):
        return Profile.objects.filter(user=user)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, )
    group = models.ForeignKey(Groups, on_delete=models.CASCADE, null=True, blank=True)

    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, null=True, blank=True)
    related_area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)
    related_region = models.ForeignKey(Region, on_delete=models.CASCADE)

    is_student = models.BooleanField(default=True)
    is_teacher = models.BooleanField(default=False)
    is_executive = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    created_by = models.ForeignKey(User, related_name='profile_created_by', on_delete=models.DO_NOTHING)
    objects = ProfileManager()

    def __str__(self):
        return self.user.username

    def delete(self, *args, **kwargs):
        self.user.delete()
        return super(self.__class__, self).delete(*args, **kwargs)
