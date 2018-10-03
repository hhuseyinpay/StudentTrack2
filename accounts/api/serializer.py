from django.db.models import Q
from rest_framework import serializers

from accounts.models import User, Profile, Groups, Region, Area, ClassRoom


class UserModelSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=30)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=30)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name')


class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class ListProfileSerializer(serializers.ModelSerializer):
    user = ListUserSerializer()

    class Meta:
        model = Profile
        fields = ('id', 'user', 'is_teacher', 'is_executive', 'is_admin')


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


class ProfileRetrieveUpdateDestroySeriazlizer(serializers.ModelSerializer):
    user = UserModelSerializer()
    classroom = PClassSerializer()  # CRPrimaryKeyRelatedField()
    related_area = PAreaSerializer(read_only=True)  # serializers.StringRelatedField(read_only=True)
    related_region = PRegionSerializer(read_only=True)  # serializers.StringRelatedField(read_only=True)

    group = PGroupSerializer()

    class Meta:
        model = Profile
        fields = (
            'id', 'user', 'group', 'classroom', 'related_area', 'related_region',
            'is_student', 'is_teacher', 'is_executive', 'is_admin'
        )
        read_only_fields = ('is_student', 'is_teacher', 'is_executive', 'is_admin',)

    def create(self, validated_data):
        u = validated_data['user']
        user = User.objects.create(**u)  # new user create
        current_user = self.context['user']

        group = self.validated_data['group']

        classroom = validated_data['classroom']
        area = classroom.related_area
        region = area.related_region

        pr = Profile(user=user, group=group, classroom=classroom, related_area=area, related_region=region,
                     created_by=current_user)

        if current_user.profile.is_executive:
            pr.is_teacher = validated_data.get('is_teacher', False)
        elif current_user.profile.is_admin:
            pr.is_teacher = validated_data.get('is_teacher', False)
            pr.is_executive = validated_data.get('is_executive', False)

        # hem öğrenci hem yetkili olmak yok öyle ;)
        if pr.is_teacher or pr.is_executive or pr.is_admin:
            pr.is_student = False

        pr.save()
        return pr

    def update(self, instance, validated_data):
        """
        user için ayrı admin için ayrı serializer oluşturulmalı. şuanda spagetti oldu kod :(
        """
        current_user = self.context['user']
        if current_user.profile.is_executive:
            instance.is_teacher = validated_data.get('is_teacher', False)
        elif current_user.profile.is_admin:
            instance.is_teacher = validated_data.get('is_teacher', False)
            instance.is_executive = validated_data.get('is_executive', False)

        if instance.is_teacher or instance.is_executive or instance.is_admin:
            instance.is_student = False

        if current_user.profile.is_teacher or current_user.profile.is_executive or current_user.profile.is_admin:
            group = validated_data.get('group', instance.group)
            if group:
                instance.group = group

        c = validated_data.get('classroom', None)  # if classroom change
        if c:
            c = ClassRoom.objects.get(id=c['id'])
            instance.classroom = c
            instance.related_area = c.related_area
            instance.related_region = c.related_area.related_region

        instance.save()
        validated_user = validated_data.get('user')
        if validated_user:
            u = User.objects.get(profile=instance)
            u.username = validated_user.get('username', u.username)
            u.password = validated_user.get('password', u.password)

            u.first_name = validated_user.get('first_name', u.first_name)
            u.last_name = validated_user.get('last_name', u.last_name)
            u.save()

        return instance


#  normalde ProfileRetrieveUpdateDestroySeriazlizer create için yetiyor ancak classroom seçiminde yetki durumunu
# değerlendirmek için inherit edip classroom fieldını override ettim.

class CRPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        user = self.context['user']
        profile = user.profile

        return ClassRoom.objects.filter(
            Q(related_area__related_region__admins=user) |
            Q(related_area__executives=user) |
            Q(teachers=user)
        ).distinct()


class ProfileCreateSerializer(ProfileRetrieveUpdateDestroySeriazlizer):
    classroom = CRPrimaryKeyRelatedField()
    group = serializers.PrimaryKeyRelatedField(queryset=Groups.objects.all())


class ProfileModelSerializer(serializers.ModelSerializer):
    user = UserModelSerializer()
    classroom = PClassSerializer(read_only=True)
    related_area = PAreaSerializer(read_only=True)
    related_region = PRegionSerializer(read_only=True)

    group = PGroupSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = (
            'id', 'user', 'group', 'classroom', 'related_area', 'related_region',
            'is_student', 'is_teacher', 'is_executive', 'is_admin'
        )
        read_only_fields = ('is_student', 'is_teacher', 'is_executive', 'is_admin',)

    def update(self, instance, validated_data):
        validated_user = validated_data.get('user')
        if validated_user:
            u = User.objects.get(profile=instance)
            u.username = validated_user.get('username', u.username)
            u.password = validated_user.get('password', u.password)

            u.first_name = validated_user.get('first_name', u.first_name)
            u.last_name = validated_user.get('last_name', u.last_name)
            u.save()

        instance.save()
        return instance


class AdminProfileModelSerializer(serializers.ModelSerializer):
    user = UserModelSerializer()
    classroom = PClassSerializer()
    related_area = PAreaSerializer(read_only=True)
    related_region = PRegionSerializer(read_only=True)

    group = PGroupSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = (
            'id', 'user', 'group', 'classroom', 'related_area', 'related_region',
            'is_student', 'is_teacher', 'is_executive', 'is_admin'
        )

    def create(self, validated_data):
        u = validated_data['user']
        password = u.pop('password')

        user = User(**u)  # new user create
        user.set_password(password)
        user.save()

        current_user = self.context['current_user']

        pr = Profile(user=user, created_by=current_user)

        pr.group = self.validated_data['group']

        classroom = validated_data['classroom']
        pr.classroom = classroom
        pr.related_area = classroom.related_area
        pr.related_region = classroom.related_area.related_region

        pr.is_student = validated_data.get('is_student', True)  # In default all profiles are student
        pr.is_teacher = validated_data.get('is_teacher', False)
        pr.is_executive = validated_data.get('is_executive', False)
        pr.is_admin = validated_data.get('is_admin', False)

        pr.save()
        return pr

    def update(self, instance, validated_data):
        instance.is_student = validated_data.get('is_student', instance.is_student)
        instance.is_teacher = validated_data.get('is_teacher', instance.is_teacher)
        instance.is_executive = validated_data.get('is_executive', instance.is_executive)
        instance.is_admin = validated_data.get('is_admin', instance.admin)

        instance.group = validated_data.get('group', instance.group)

        c = validated_data.get('classroom', None)  # if classroom change
        if c:
            c = ClassRoom.objects.get(id=c['id'])
            instance.classroom = c
            instance.related_area = c.related_area
            instance.related_region = c.related_area.related_region

        instance.save()
        validated_user = validated_data.get('user')
        if validated_user:
            u = User.objects.get(profile=instance)
            u.username = validated_user.get('username', u.username)
            u.password = validated_user.get('password', u.password)

            u.first_name = validated_user.get('first_name', u.first_name)
            u.last_name = validated_user.get('last_name', u.last_name)
            u.save()

        return instance


class AdminProfileCreateSerializer(AdminProfileModelSerializer):
    classroom = serializers.PrimaryKeyRelatedField(queryset=ClassRoom.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Groups.objects.all())
