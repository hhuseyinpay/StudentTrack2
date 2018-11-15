from django_filters.rest_framework import FilterSet
from django_filters import DateFilter

from daily_study.models import DailyStudy


class DailyStudyCreatedDayFilter(FilterSet):
    begining = DateFilter(field_name='created_day', lookup_expr='gte')
    end = DateFilter(field_name='created_day', lookup_expr='lte')

    class Meta:
        model = DailyStudy
        fields = {'begining', 'end', 'is_validated', 'user', 'user__classroom', 'user__classroom__area'}
