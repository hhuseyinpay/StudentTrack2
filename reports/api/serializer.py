from rest_framework import serializers


class DailyStudyReportGeneratorSerialzier(serializers.Serializer):
    begining = serializers.DateField()
    end = serializers.DateField()

    def validate(self, data):
        if data['begining'] > data['end']:
            raise serializers.ValidationError("Begining must be bigger than end")
        return data
