from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueTogetherValidator
from rest_framework import serializers

from ..models import Content, Syllabus, UserSyllabus
from course.models import Course

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


class ContentModelSerializer_OLD(serializers.ModelSerializer):
    # id = serializers.IntegerField(required=False)

    class Meta:
        model = Content
        fields = ('id', 'week', 'name', 'description')


class SyllabusModelSerializer(serializers.ModelSerializer):
    contents = ContentModelSerializer_OLD(required=True, many=True)
    course = CourseSerializer()

    class Meta:
        model = Syllabus
        fields = ('id', 'level', 'course', 'contents')


class UserSyllabusModelSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = UserSyllabus
        fields = ('id', 'user', 'content', 'is_validated', 'validator_user')
        read_only_fields = ('valdator_user', 'is_validated')
        validators = [
            UniqueTogetherValidator(
                queryset=UserSyllabus.objects.all(),
                fields=('user', 'content')
            )
        ]


class AdminUserSyllabusModelSerializer(UserSyllabusModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())


class UserSyllabusNotValidatedSerializer(serializers.ModelSerializer):
    content = ContentModelSerializer_OLD()

    class Meta:
        model = UserSyllabus
        fields = ('id', 'user', 'content', 'is_validated', 'validator_user')


class UserSyllabusValidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSyllabus
        fields = ('id', 'is_validated', 'validator_user')
        read_only_fields = ('id', 'validator_user')

    def update(self, instance, validated_data):
        validate = validated_data.get('is_validated')

        # daha önce onaylanmadıysa ve şimdi onaylanıyorsa
        if not instance.is_validated and validate:
            instance.is_validated = True
            instance.validator_user = self.context['user']

        # daha önce onaylandıysa ve onay kaldırılıyorsa
        elif instance.is_validated and not validate:
            instance.is_validated = False
            instance.validator_user = self.context['user']

        instance.save()
        return instance
