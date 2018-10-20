from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.accounts.models import User, Profile, Groups, Region, Area, ClassRoom


class UserModelSerializer(serializers.ModelSerializer):
    username = serializers.CharField(min_length=3, max_length=30, validators=[
        UniqueValidator(queryset=User.objects.all(), message="Bu kullanıcı Adı başkası tarafından alındı.")
    ])
    first_name = serializers.CharField(min_length=2, max_length=50)
    last_name = serializers.CharField(min_length=2, max_length=30)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

# *********************************************

class RegionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'


class AreaModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'

    region = RegionModelSerializer()


class ClassRoomModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoom
        fields = '__all__'

    area = AreaModelSerializer()


class MyAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('id', 'name')


class MyClassRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoom
        fields = ('id', 'name')


# ***********************************************
class ProfileModelSerializer(serializers.ModelSerializer):
    user = UserModelSerializer()

    class Meta:
        model = Profile
        fields = (
            'id', 'user', 'phone_number', 'joined_date', 'group', 'classroom',
            'is_student', 'is_teacher', 'is_executive', 'is_admin'
        )
        read_only_fields = (
            'is_student', 'is_teacher', 'is_executive', 'is_admin',
        )

    def create(self, validated_data):
        u = validated_data.pop('user')
        password = u.pop('password')

        user = User(**u)  # new user create
        user.set_password(password)
        user.save()
        for i, v in validated_data.items():
            print("    ", i, ": ", v)
        return Profile.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        validated_user = validated_data.pop('user')
        if validated_user:
            u = User.objects.get(profile=instance)
            u.username = validated_user.get('username', u.username)
            if validated_user.get('password'):
                u.set_password(validated_user.get('password'))

            u.first_name = validated_user.get('first_name', u.first_name)
            u.last_name = validated_user.get('last_name', u.last_name)
            u.save()

        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.joined_date = validated_data.get('joined_date', instance.joined_date)
        instance.group = validated_data.get('group', instance.group)

        instance.is_student = validated_data.get('is_student', instance.is_student)
        instance.is_teacher = validated_data.get('is_teacher', instance.is_teacher)
        instance.is_executive = validated_data.get('is_executive', instance.is_executive)
        # instance.is_admin = validated_data.get('is_admin', instance.admin)

        instance.classroom = validated_data.get('classroom', instance.classroom)

        instance.save()
        return instance


class StudentProfileSerializer(ProfileModelSerializer):
    classroom = serializers.PrimaryKeyRelatedField(required=True, queryset=ClassRoom.objects.all())
    joined_date = serializers.DateField(read_only=True)


class AdminProfileSerializer(ProfileModelSerializer):
    group = serializers.PrimaryKeyRelatedField(required=False, queryset=Groups.objects.all())
    joined_date = serializers.DateField(required=True)


class AdminMakeStudentSeriazlier(serializers.Serializer):
    classroom = serializers.PrimaryKeyRelatedField(queryset=ClassRoom.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Groups.objects.all())


class AdminChangeClassRoomSerializer(serializers.Serializer):
    classroom = serializers.PrimaryKeyRelatedField(required=False, queryset=ClassRoom.objects.all())


class AdminChangeAreaSerializer(serializers.Serializer):
    area = serializers.PrimaryKeyRelatedField(required=False, queryset=ClassRoom.objects.all())


class AdminClassroomTeacherSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(profile__is_teacher=True))


class AdminClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoom
        fields = '__all__'


class AdminAreaExcutiveSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(profile__is_executive=True))


class AdminAreaSeriazlier(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'
