from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from student.account.models import User
from student.course.models import CourseGroups


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'user_type')


class UserModelSerializer(serializers.ModelSerializer):
    # user_type = serializers.CharField(source='get_user_type_display', read_only=True)
    username = serializers.CharField(min_length=3, max_length=30, required=True,
                                     validators=[UniqueValidator(
                                         queryset=User.objects.all(),
                                         message='This username already in use'
                                     )])
    first_name = serializers.CharField(min_length=3, max_length=30, required=True)
    last_name = serializers.CharField(min_length=3, max_length=30, required=True)
    password = serializers.CharField(min_length=3, max_length=30, write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'phone_number',
                  'user_type', 'classroom', 'course_group', 'joined_date')
        extra_kwargs = {
            'user_type': {'read_only': True}, 'classroom': {'read_only': True},
            'course_group': {'read_only': True}, 'joined_date': {'read_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class AdminUserModelSerializer(UserModelSerializer):
    joined_date = serializers.DateField(required=True)
    course_group = serializers.PrimaryKeyRelatedField(queryset=CourseGroups.objects.all(), required=True)

    # user_type = serializers.CharField(source='get_user_type_display', read_only=True) # user tyep'ı string'e çeviriyor

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'phone_number',
                  'user_type', 'classroom', 'course_group', 'joined_date')
        extra_kwargs = {'password': {'write_only': True},
                        'user_type': {'read_only': True},
                        'classroom': {'read_only': True}}

