from rest_framework import serializers

from accounts.models import User, Profile, Groups, Region, Area, ClassRoom


class UserModelSerializer(serializers.ModelSerializer):
    username = serializers.CharField(min_length=3, max_length=30)
    first_name = serializers.CharField(min_length=2, max_length=50)
    last_name = serializers.CharField(min_length=2, max_length=30)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name')


# *********************************************

class PClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoom
        fields = ('id', 'name')


class PAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('id', 'name')


class PRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'name')


class PGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Groups
        fields = ('id', 'name', 'description')


class ProfileModelSerializer(serializers.ModelSerializer):
    user = UserModelSerializer()
    classroom = PClassSerializer(read_only=True)
    related_area = PAreaSerializer(read_only=True)
    related_region = PRegionSerializer(read_only=True)

    group = PGroupSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = (
            'id', 'user', 'phone_number', 'joined_date', 'group', 'classroom', 'related_area', 'related_region',
            'is_student', 'is_teacher', 'is_executive', 'is_admin'
        )
        read_only_fields = ('joined_date', 'is_student', 'is_teacher', 'is_executive', 'is_admin',)

    def update(self, instance, validated_data):
        validated_user = validated_data.get('user')
        if validated_user:
            u = User.objects.get(profile=instance)
            u.username = validated_user.get('username', u.username)
            if validated_user.get('password', None):
                u.set_password(validated_user.get('password'))

            u.first_name = validated_user.get('first_name', u.first_name)
            u.last_name = validated_user.get('last_name', u.last_name)
            u.save()
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()
        return instance


class AdminProfileModelSerializer(serializers.ModelSerializer):
    user = UserModelSerializer()
    classroom = PClassSerializer()
    related_area = PAreaSerializer()
    related_region = PRegionSerializer()
    group = PGroupSerializer()

    class Meta:
        model = Profile
        fields = (
            'id', 'user', 'phone_number', 'joined_date', 'group', 'classroom', 'related_area', 'related_region',
            'is_student', 'is_teacher', 'is_executive', 'is_admin'
        )
        read_only_fields = (
            'is_student', 'is_teacher', 'is_executive', 'is_admin', 'classroom', 'related_area', 'related_region'
        )

    def create(self, validated_data):
        u = validated_data.pop('user')
        password = u.pop('password')

        user = User(**u)  # new user create
        user.set_password(password)
        user.save()

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
        instance.related_area = validated_data.get('related_area', instance.related_area)
        instance.related_region = validated_data.get('related_region', instance.related_region)

        instance.save()
        return instance


class AdminProfileCreateSerializer(AdminProfileModelSerializer):
    classroom = serializers.PrimaryKeyRelatedField(read_only=True)
    related_area = serializers.PrimaryKeyRelatedField(read_only=True)
    related_region = serializers.PrimaryKeyRelatedField(read_only=True)
    group = serializers.PrimaryKeyRelatedField(required=False, queryset=Groups.objects.all())
    joined_date = serializers.DateField(required=True)


class AdminMakeStudentSeriazlier(serializers.Serializer):
    classroom = serializers.PrimaryKeyRelatedField(queryset=ClassRoom.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Groups.objects.all())


class AdminChangeClassRoomSerializer(serializers.Serializer):
    classroom = serializers.PrimaryKeyRelatedField(required=False, queryset=ClassRoom.objects.all())


class AdminChangeAreaSerializer(serializers.Serializer):
    related_area = serializers.PrimaryKeyRelatedField(required=False, queryset=ClassRoom.objects.all())


class AdminClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoom
        fields = '__all__'


class AdminAreaSeriazlier(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'
