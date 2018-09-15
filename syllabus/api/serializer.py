from datetime import datetime

from rest_framework.validators import UniqueTogetherValidator
from rest_framework import serializers

from ..models import Content, Syllabus, UserSyllabus
from base.models import Course


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'name')


class SyllabusListSerializer(serializers.ModelSerializer):
    course = CourseSerializer()

    class Meta:
        model = Syllabus
        fields = ('id', 'level', 'course')


class ContentModelSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(required=False)

    class Meta:
        model = Content
        fields = ('id', 'week', 'name', 'description')


class SyllabusModelSerializer(serializers.ModelSerializer):
    contents = ContentModelSerializer(required=True, many=True)
    course = CourseSerializer()

    class Meta:
        model = Syllabus
        fields = ('id', 'level', 'course', 'contents')


class UserSyllabusModelSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserSyllabus
        fields = ('id', 'user', 'content', 'status', 'validator_user')
        read_onyl_files = ('id', 'valdator_user', 'status')
        validators = [
            UniqueTogetherValidator(
                queryset=UserSyllabus.objects.all(),
                fields=('user', 'content')
            )
        ]


class UserSyllabusListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSyllabus
        # current_user = self.context['user']
