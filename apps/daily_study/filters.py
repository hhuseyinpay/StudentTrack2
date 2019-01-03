from django_filters.rest_framework import FilterSet, BooleanFilter, DateFilter

from daily_study.models import DailyStudy


class DailyStudyCreatedDayFilter(FilterSet):
    begining = DateFilter(field_name='created_day', lookup_expr='gte')
    end = DateFilter(field_name='created_day', lookup_expr='lte')
    is_validated = BooleanFilter(method='is_validated_filter')

    class Meta:
        model = DailyStudy
        fields = {'begining', 'end', 'is_validated', 'user', 'user__classroom', 'user__classroom__area'}

    def is_validated_filter(self, queryset, name, value):
        """
        student dailystudyleri gece otomatik oluşturuluyor ve is_validated false oluyor.
        Ancak student dailystudy'i daha doldurmadı ve bütün studyler default oalrak 0 geldi.

        dailystudy onay ekranında görünen daily studylerin student tarafından doldurulduğunu tespit etmek için
        updated__isnull kontrolü ekledim.
        Otomatik eklenen dailystudyler student tarafından update edildikten sonra onay ekranına düşecek..
        """
        if value == False:
            return queryset.filter(updated__isnull=False, is_validated=False)
        else:
            return queryset
