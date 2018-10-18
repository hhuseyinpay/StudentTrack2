from django.urls import path

from base.api.views import UserGroupCourseListAPIView, GroupListAPIView

urlpatterns = [
    path('user/<int:user>/', UserGroupCourseListAPIView.as_view()),
    path('allgroups', GroupListAPIView.as_view())
]
