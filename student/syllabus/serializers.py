from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from rest_framework.validators import UniqueTogetherValidator

from student.course.models import Course
from .models import Content, Syllabus, UserSyllabus

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


class UserContentSerializer(serializers.ModelSerializer):
    user_syllabus_id = serializers.PrimaryKeyRelatedField(read_only=True)
    is_done = serializers.BooleanField()
    is_validated = serializers.BooleanField()
    content_name = serializers.CharField(source='name')

    class Meta:
        model = Content
        exclude = ('description',)


class UserSyllabusSerializerV2(serializers.ModelSerializer):
    user = serializers.HiddenField(default=CurrentUserDefault())
    content_name = serializers.StringRelatedField(source='content', read_only=True)

    class Meta:
        model = UserSyllabus
        fields = '__all__'
        read_only_fields = ('valdator_user', 'validate_time', 'is_validated')
        validators = [
            UniqueTogetherValidator(
                queryset=UserSyllabus.objects.all(),
                fields=('user', 'content'),
                message='Aynı kurdan birden fazla oluşturulamaz.'
            )
        ]


class AdminUserSyllabusSerializerV2(UserSyllabusSerializerV2):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user_full_name = serializers.SerializerMethodField(read_only=True)

    def get_user_full_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name


class AdminUserSyllabusBulkUpdateSeriazlier(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(min_value=0))
