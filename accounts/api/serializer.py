from django.db.models import Q
from rest_framework import serializers

from accounts.models import User, Profile, Region, Area, ClassRoom


class UserModelSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(max_length=30, required=True)
    last_name = serializers.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')
        write_only_fields = ('password',)


class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class ListProfileSerializer(serializers.ModelSerializer):
    user = ListUserSerializer()

    class Meta:
        model = Profile
        fields = ('id', 'user', 'is_teacher', 'is_executive', 'is_admin')


class ClassRoomBasicModelSerializer(serializers.ModelSerializer):
    teachers = serializers.StringRelatedField(many=True)
    related_area = serializers.StringRelatedField()

    class Meta:
        model = ClassRoom
        fields = ('id', 'name', 'teachers', 'related_area')


class ProfileModelSerializer(serializers.ModelSerializer):
    user = UserModelSerializer()
    classroom = ClassRoomBasicModelSerializer()

    class Meta:
        model = Profile
        fields = ('user', 'classroom', 'is_teacher', 'is_executive', 'is_admin')


# *********************************************

class PClassSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=False, read_only=True)

    class Meta:
        model = ClassRoom
        fields = ('id', 'name')


class PAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoom
        fields = ('id', 'name')


class PRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoom
        fields = ('id', 'name')


class ProfileRetrieveUpdateDestroySeriazlizer(serializers.ModelSerializer):
    user = UserModelSerializer()
    classroom = PClassSerializer()  # CRPrimaryKeyRelatedField()
    # related_area = PAreaSerializer(read_only=True)  # serializers.StringRelatedField(read_only=True)
    related_region = PRegionSerializer(read_only=True)  # serializers.StringRelatedField(read_only=True)

    # is_student = serializers.BooleanField(required=False)
    # is_teacher = serializers.BooleanField(required=False)
    # is_executive = serializers.BooleanField(required=False)
    # is_admin = serializers.BooleanField(required=False)

    class Meta:
        model = Profile
        fields = (
            'id', 'user', 'classroom', 'related_area', 'related_region',
            'is_student', 'is_teacher', 'is_executive', 'is_admin'
        )
        read_only_fields = ('related_area', 'related_region', 'is_student', 'is_teacher', 'is_executive', 'is_admin',)

    def create(self, validated_data):
        u = validated_data['user']
        user = User.objects.create(**u)  # new user create
        current_user = self.context['user']

        classroom = validated_data['classroom']
        area = classroom.related_area
        region = area.related_region

        pr = Profile(user=user, classroom=classroom, related_area=area, related_region=region, created_by=current_user)

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
        current_user = self.context['user']

        if current_user.profile.is_executive:
            instance.is_teacher = validated_data.get('is_teacher', False)
        elif current_user.profile.is_admin:
            instance.is_teacher = validated_data.get('is_teacher', False)
            instance.is_executive = validated_data.get('is_executive', False)
        if instance.is_teacher or instance.is_executive or instance.is_admin:
            instance.is_student = False

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
