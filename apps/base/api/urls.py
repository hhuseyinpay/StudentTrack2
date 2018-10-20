from django.urls import path, include
from rest_framework.routers import DefaultRouter

from base.api.views import UserGroupCourseListAPIView, GroupListAPIView, GroupViewset

group_router = DefaultRouter()
group_router.register('groups', GroupViewset, 'groupviewset')

urlpatterns = [
    path('user/<int:user>/', UserGroupCourseListAPIView.as_view()),
    path('allgroups', GroupListAPIView.as_view()),
    path('', include(group_router.urls))
]
