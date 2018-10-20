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
        fields = ('id', 'user', 'content', 'is_validated', 'validator_user')
        read_onyl_files = ('id', 'valdator_user', 'is_validated')
        validators = [
            UniqueTogetherValidator(
                queryset=UserSyllabus.objects.all(),
                fields=('user', 'content')
            )
        ]


class AdminUserSyllabusModelSerializer(UserSyllabusModelSerializer):
    content = ContentModelSerializer()


class UserSyllabusNotValidatedSerializer(serializers.ModelSerializer):
    content = ContentModelSerializer()

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
