from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework import serializers

from daily_study.models import DailyStudy, Study

User = get_user_model()


class StudyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields = ('course', 'begining', 'end', 'amount')
        extra_kwargs = {
            'course': {'required': True}, 'begining': {'required': True},
            'end': {'required': True}, 'amount': {'required': True}
        }


class DailyStudyModelSerializer(serializers.ModelSerializer):
    studies = StudyModelSerializer(required=True, many=True)

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


class DailyStudyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyStudy
        fields = ('id', 'user', 'created_day', 'is_validated')


class AdminDailyStudyModelSerializer(DailyStudyModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
