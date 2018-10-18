from rest_framework import serializers

from apps.accounts.models import Region
from apps.base.models import Groups


class WeeksSerialzier(serializers.Serializer):
    begining = serializers.DateField()
    end = serializers.DateField()

    def validate(self, data):
        if data['begining'] > data['end']:
            raise serializers.ValidationError("Begining must be bigger than end")
        return data


class DailyStudyReportGeneratorSerialzier(serializers.Serializer):
    region = serializers.PrimaryKeyRelatedField(required=True, queryset=Region.objects.all())
    group = serializers.PrimaryKeyRelatedField(required=True, queryset=Groups.objects.all())
    include_teacher = serializers.BooleanField(required=True)
    weeks = WeeksSerialzier(required=True, many=True)
