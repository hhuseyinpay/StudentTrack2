from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from rest_framework.validators import UniqueTogetherValidator

from course.models import Course
from ..models import Content, Syllabus, UserSyllabus

User = get_user_model()


class LevelListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Syllabus
        fields = ('level',)


class CourseListSeriazlier(serializers.ModelSerializer):
    course = serializers.StringRelatedField()

    class Meta:
        model = Syllabus
        fields = ('id', 'course')


class ContentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'name')


class SyllabusListSerializer(serializers.ModelSerializer):
    course = CourseSerializer()

    class Meta:
        model = Syllabus
        fields = ('id', 'level', 'course')


class SyllabusModelSerializer(serializers.ModelSerializer):
    contents = ContentModelSerializer(required=True, many=True)
    course = CourseSerializer()

    class Meta:
        model = Syllabus
        fields = ('id', 'level', 'course', 'contents')


class UserSyllabusModelSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        model = UserSyllabus
        fields = ('id', 'user', 'content', 'is_validated', 'validate_time', 'validator_user')
        read_only_fields = ('valdator_user', 'validate_time', 'is_validated')
        validators = [
            UniqueTogetherValidator(
                queryset=UserSyllabus.objects.all(),
                fields=('user', 'content'),
                message='Aynı kurdan birden fazla oluşturulamaz.'
            )
        ]


class AdminUserSyllabusModelSerializer(UserSyllabusModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
