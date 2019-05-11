from django.contrib.auth import get_user_model
from rest_framework import serializers

from student.location.models import Region, Area, ClassRoom

# *********************************************
User = get_user_model()


class ClassRoomModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoom
        fields = '__all__'
        extra_kwargs = {'teachers': {'read_only': True}}  # , 'area': {'read_only': True}}


class ClassRoomListSerializer(serializers.ModelSerializer):
    area = serializers.StringRelatedField()

    class Meta:
        model = ClassRoom
        fields = ('id', 'name', 'area')
