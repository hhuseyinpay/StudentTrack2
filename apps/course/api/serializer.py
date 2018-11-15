from rest_framework import serializers

from course.models import CourseGroups, Course


class CourseGroupModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseGroups
        fields = '__all__'


class CourseGroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseGroups
        fields = ('id', 'name')


class CourseModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
