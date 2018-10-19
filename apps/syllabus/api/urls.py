from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SyllabusLevelListAPIView, SyllabusAllListAPIView, UserSyllabusUserViewSet, \
    SyllabusLevelCourseAPIView, UserSyllabusAPIView, UserSyllabusNotValidatedAPIView, AdminUSAPIView, \
    AdminUSValidateAPIView, AdminUSNotValidatedAPIView

router = DefaultRouter()
router.register('me', UserSyllabusUserViewSet, 'UserSyllabus')

urlpatterns = [
    path('', include(router.urls)),

    path('list', SyllabusAllListAPIView.as_view(), name="syllabus list all"),
    path('level/<int:level>/', SyllabusLevelListAPIView.as_view(), name="syllabus list with level"),
    path('level/<int:level>/course/<int:course>/', SyllabusLevelCourseAPIView.as_view()),
    path('user/me/level/<int:level>/course/<int:course>/', UserSyllabusAPIView.as_view()),

    path('user/me/notvalidated/', UserSyllabusNotValidatedAPIView.as_view()),

    path('admin/user/<int:user>/level/<int:level>/course/<int:course>/', AdminUSAPIView.as_view()),
    path('admin/validate/<int:id>/', AdminUSValidateAPIView.as_view()),
    path('admin/notvalidated/user/<int:user>/', AdminUSNotValidatedAPIView.as_view())
]