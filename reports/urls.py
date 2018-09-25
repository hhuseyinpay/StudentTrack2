from django.urls import path

from .views import report_list, report_download

urlpatterns = [
    path('daily_study/mountly/', report_list, name='report_list'),
    path('daily_study/mountly/<str:report_name>/', report_download, name='report_download')
]
