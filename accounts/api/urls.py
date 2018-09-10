from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProfileListAPIView, ProfileViewSet, \
    ClassRoomProfileListAPIView, AreaProfileListAPIView, \
    RegionProfileListAPIView, ListAllProfileAPIView, ProfileRetrieveUpdateDestroyAPIView, ProfileCreateAPIView

router = DefaultRouter()
router.register('profile', ProfileViewSet, 'profileviewset')

urlpatterns = [
    path('profile/me/', ProfileListAPIView.as_view(), name="user profile retrieve"),

    # path('edit/', include(router.urls), name="profile-detail"),
    path('profile/create/', ProfileCreateAPIView.as_view()),
    path('profile/edit/<int:id>/', ProfileRetrieveUpdateDestroyAPIView.as_view()),

    path('profile/all/', ListAllProfileAPIView.as_view()),
    path('profile/classroom/<int:classroom>/', ClassRoomProfileListAPIView.as_view()),
    path('profile/area/<int:area>/', AreaProfileListAPIView.as_view()),
    path('profile/region/<int:region>/', RegionProfileListAPIView.as_view()),

    # path('classroom/'),
    # path('area/'),
    # path('region/'),

    # path('create/', ProfileCreateAPIView.as_view(), name="user profile create"),
    # path('edit/<int:id>/', ProfileRetrieveUpdateDestroyAPIView.as_view(), name="user profile retrieve-update-delete"),
]
