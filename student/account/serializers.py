from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from student.account.models import User
from student.course.models import CourseGroups
from student.location.models import ClassRoom, Area
from student.course.serializers import CourseGroupListSerializer
from student.location.serializers import ClassRoomListSerializer



################### V2

class UserModelSerializerV2(serializers.ModelSerializer):
    username = serializers.CharField(
        min_length=3, max_length=30, required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all(), message='This username already in use')
        ])
    phone_number = serializers.CharField(min_length=10, max_length=11, required=False)
    course_group = CourseGroupListSerializer(read_only=True)
    classroom = ClassRoomListSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'phone_number',
                  'user_type', 'classroom', 'course_group', 'joined_date')
        extra_kwargs = {
            'user_type': {'read_only': True}, 'joined_date': {'read_only': True}
        }


class AdminUserModelSerializerV2(UserModelSerializerV2):
    user_type = serializers.IntegerField(read_only=True)
    password = serializers.CharField(min_length=3, max_length=30, write_only=True, required=False)
    course_group_id = serializers.PrimaryKeyRelatedField(queryset=CourseGroups.objects.all(), source='course_group',
                                                         write_only=True, required=True)
    classroom_id = serializers.PrimaryKeyRelatedField(queryset=ClassRoom.objects.all(), source='classroom',
                                                      write_only=True, required=False)

    class Meta:
        model = User
        fields = UserModelSerializerV2.Meta.fields + ('course_group_id', 'password', 'classroom_id')

    def update(self, instance, validated_data):
        """
        passwordu başka bi serializer ile alacağım için buna gerek yok
        ama olsun bu da dursun, sonra akıl karışıklığı olmasın ;)
        """
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class AdminStudentSerializer(AdminUserModelSerializerV2):
    classroom_id = serializers.PrimaryKeyRelatedField(queryset=ClassRoom.objects.all(), source='classroom',
                                                      write_only=True, required=True)


class AdminTeacherSerializer(AdminUserModelSerializerV2):
    assigned_classroom_id = serializers.PrimaryKeyRelatedField(queryset=ClassRoom.objects.all(), write_only=True,
                                                               required=True)

    class Meta:
        model = User
        fields = UserModelSerializerV2.Meta.fields + ('assigned_classroom_id',)


class AdminExecutiveSerializer(AdminUserModelSerializerV2):
    assigned_area_id = serializers.PrimaryKeyRelatedField(queryset=Area.objects.all(), write_only=True, required=True)

    class Meta:
        model = User
        fields = UserModelSerializerV2.Meta.fields + ('assigned_area_id',)


class PasswordChangeSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=3, max_length=30, required=True, write_only=True)

    class Meta:
        model = User
        fields = ('password',)

    def update(self, instance, validated_data):
        password = validated_data['password']
        instance.set_password(password)
        instance.save()

        return instance
