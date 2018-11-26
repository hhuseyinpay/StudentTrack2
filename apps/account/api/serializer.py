from rest_framework import serializers

from account.models import User
from course.models import CourseGroups
from location.models import ClassRoom


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name')


class UserModelSerializer(serializers.ModelSerializer):
    # user_type = serializers.CharField(source='get_user_type_display', read_only=True)
    username = serializers.CharField(min_length=3, max_length=30, required=True)
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


class AdminMakeStudentSeriazlier(serializers.Serializer):
    classroom = serializers.PrimaryKeyRelatedField(queryset=ClassRoom.objects.all())


class AdminChangeClassRoomSerializer(serializers.Serializer):
    classroom = serializers.PrimaryKeyRelatedField(queryset=ClassRoom.objects.all())


class AdminChangeAreaSerializer(serializers.Serializer):
    area = serializers.PrimaryKeyRelatedField(required=False, queryset=ClassRoom.objects.all())
