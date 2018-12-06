from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import UserManager
from django.utils.timezone import now

from course.models import CourseGroups


class CustomUserManager(UserManager):
    def get_admins(self):
        return User.objects.filter(user_type=User.ADMIN)


class User(AbstractUser):
    ADMIN = 1
    EXECUTIVE = 2
    TEACHER = 4
    STUDENT = 8

    USER_TYPE_CHOICES = (
        (ADMIN, 'İl Vakfı'),
        (EXECUTIVE, 'İlçe Vakfı'),
        (TEACHER, 'Kat Vakfı'),
        (STUDENT, 'Talebe')
    )
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, null=True, blank=True)
    phone_regex = RegexValidator(regex=r'^(05)[0-9][0-9]([0-9]){7}$',
                                 message="Format hatası. Telefon numarası şu formatta olmalı:'05515524294'")
    phone_number = models.CharField(validators=[phone_regex], max_length=11, blank=True)  # validators should be a list

    created_by = models.ForeignKey("self", related_name='user_creator', on_delete=models.DO_NOTHING, null=True)
    classroom = models.ForeignKey("location.ClassRoom", related_name="students", on_delete=models.CASCADE, null=True,
                                  blank=True, default=None, db_index=True)
    course_group = models.ForeignKey(CourseGroups, on_delete=models.CASCADE, null=True, blank=True)
    joined_date = models.DateField(default=now)

    objects = CustomUserManager()

    def is_admin(self):
        return self.user_type == self.ADMIN

    def is_executive(self):
        return self.user_type == self.EXECUTIVE

    def is_teacher(self):
        return self.user_type == self.TEACHER

    def is_student(self):
        return self.user_type == self.STUDENT

    def is_new(self):
        return self.user_type is None or (self.user_type == User.STUDENT and self.classroom is None)

    def has_group(self):
        return self.course_group is not None
