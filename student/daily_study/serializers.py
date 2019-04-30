from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework import serializers

from .models import DailyStudy, Study

User = get_user_model()


class StudyModelSerializer(serializers.ModelSerializer):
    course_name = serializers.StringRelatedField(source='course', read_only=True)

    class Meta:
        model = Study
        fields = ('course_name', 'course', 'begining', 'end', 'amount')
        extra_kwargs = {
            'course': {'required': True}, 'begining': {'required': True},
            'end': {'required': True}, 'amount': {'required': True}
        }


class DailyStudyModelSerializer(serializers.ModelSerializer):
    studies = StudyModelSerializer(required=True, many=True)
    user_full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DailyStudy
        fields = '__all__'
        read_only_fields = (
            'created_day', 'timestamp', 'updated', 'user', 'is_validated', 'validate_time', 'validator_user'
        )

    def create(self, validated_data):
        studies = validated_data.pop('studies', [])
        ds = DailyStudy.objects.create(**validated_data)
        for study in studies:
            Study.objects.create(daily_study=ds, **study)
        return ds

    def update(self, instance, validated_data):
        items = validated_data.get('studies')
        # önce tüm çalışmaları sil. sonra yeniden oluştur.
        instance.studies.all().delete()
        for item in items:
            Study.objects.create(daily_study=instance, **item)

        instance.updated = now()
        instance.save()
        return instance

    def get_user_full_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name


class DailyStudyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyStudy
        fields = ('id', 'user', 'created_day', 'is_validated')


class AdminDailyStudyModelSerializer(DailyStudyModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)


class AdminDailyStudyListSerializerV2(serializers.ModelSerializer):
    user_full_name = serializers.SerializerMethodField(read_only=True)
    classroom = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DailyStudy
        fields = '__all__'

    def get_user_full_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name

    def get_classroom(self, obj):
        return str(obj.user.classroom)
