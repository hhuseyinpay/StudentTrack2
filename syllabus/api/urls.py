from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SyllabusLevelListAPIView, SyllabusAllListAPIView, UserSyllabusUserViewSet, SyllabusLevelCourseAPIView

router = DefaultRouter()
router.register('me', UserSyllabusUserViewSet, 'UserSyllabus')

urlpatterns = [
    path('', include(router.urls)),

    path('list', SyllabusAllListAPIView.as_view(), name="syllabus list all"),
    path('level/<int:level>/', SyllabusLevelListAPIView.as_view(), name="syllabus list with level"),
    path('level/<int:level>/course/<int:course>/', SyllabusLevelCourseAPIView.as_view())
    # path('me/id-list/', UserSyllabusListCreateAPIView.as_view(), name="usersyllabus list create")
]
