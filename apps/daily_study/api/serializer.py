from datetime import datetime

from django.utils.timezone import now
from rest_framework import serializers

from daily_study.models import DailyStudy, Study


class StudyModelSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Study
        fields = ('id', 'course', 'begining', 'end', 'amount',)


class DailyStudyModelSerializer(serializers.ModelSerializer):
    studies = StudyModelSerializer(many=True, required=True)

    class Meta:
        model = DailyStudy
        fields = ('id', 'user', 'is_validated', 'validator_user', 'validate_time', 'timestamp', 'updated', 'studies',)
        read_only_fields = ('id', 'user', 'is_validated', 'validator_user', 'validate_time', 'timestamp', 'updated',)

    def create(self, validated_data):
        try:
            d = DailyStudy.objects.get(user=self.context['user'], created_day=datetime.today())
        except DailyStudy.DoesNotExist:
            d = None
        # bugün yeni bir dailystudy oluşturulduysa error
        if d is not None:
            # raise serializers.ValidationError("You have created daily study today")
            raise serializers.ValidationError("Bu günkü çeteleni doldurdun.")

        studies = validated_data.pop('studies')

        # get the user from view and initial is_validated is false
        ds = DailyStudy.objects.create(user=self.context['user'], **validated_data)

        for study in studies:
            Study.objects.create(studies=ds, **study)
        return ds

    def update(self, instance, validated_data):
        instance.updated = now()
        instance.save()
        items = validated_data.get('studies')
        for item in items:
            item_id = item.get('id', None)
            if item_id:
                inv_item = Study.objects.get(id=item_id, studies=instance)
                inv_item.begining = item.get('begining', inv_item.begining)
                inv_item.end = item.get('end', inv_item.end)
                inv_item.amount = item.get('amount', inv_item.amount)
                inv_item.save()

        instance.save()
        return instance


class DailyStudyValidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyStudy
        fields = ('id', 'is_validated', 'validator_user', 'validate_time', 'timestamp', 'updated',)
        read_only_fields = ('validator_user', 'validate_time', 'timesampt', 'updated',)

    def update(self, instance, validated_data):
        validate = validated_data.get('is_validated')

        # daha önce onaylanmadıysa ve şimdi onaylanıyorsa
        if not instance.is_validated and validate:
            instance.is_validated = True
            instance.validator_user = self.context['user']
            instance.validate_time = now()

        # daha önce onaylandıysa ve onay kaldırılıyorsa
        elif instance.is_validated and not validate:
            instance.is_validated = False
            instance.validator_user = self.context['user']
            instance.validate_time = now()

        instance.save()
        return instance
