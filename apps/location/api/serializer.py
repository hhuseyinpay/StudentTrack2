from django.contrib.auth import get_user_model
from rest_framework import serializers

from location.models import Region, Area, ClassRoom

# *********************************************
User = get_user_model()


class RegionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'


class AreaModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'
        extra_kwargs = {'executives': {'read_only': True}, 'region': {'read_only': True}}


class ClassRoomModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoom
        fields = '__all__'
        extra_kwargs = {'teachers': {'read_only': True}, 'area': {'read_only': True}}


class AreaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('id', 'name')


class ClassRoomListSerializer(serializers.ModelSerializer):
    area = serializers.StringRelatedField()

    class Meta:
        model = ClassRoom
        fields = ('id', 'name', 'area')


class AdminClassroomTeacherSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(user_type=User.TEACHER))


class AdminAreaExcutiveSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(user_type=User.EXECUTIVE))
