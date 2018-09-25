from django.urls import path

from .views import DailyStudyReportGeneratorAPIView

urlpatterns = [
    path('genarate/daily_study/', DailyStudyReportGeneratorAPIView.as_view())
]
