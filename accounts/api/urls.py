from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProfileViewSet, ListAllProfileAPIView, UserLoginAPIView, \
    AdminGroupList, AdminProfileViewSet,AdminClassroomViewSet, \
    AdminAreaViewset

user_router = DefaultRouter()
user_router.register('', ProfileViewSet, 'profileviewset')

admin_router = DefaultRouter()
admin_router.register('profile', AdminProfileViewSet, 'admin_profile_viewset')

admin_router.register('classroom', AdminClassroomViewSet, 'admin_classroomviewset')
admin_router.register('area', AdminAreaViewset, 'admin-areaviewset')

urlpatterns = [
    path('profile/', include(user_router.urls)),
    path('login/', UserLoginAPIView.as_view()),
    # path('profile/me', ProfileListAPIView.as_view(), name="user profile retrieve"),

    # path('edit/', include(router.urls), name="profile-detail"),
    # path('profile/edit/<int:id>/', ProfileRetrieveUpdateDestroyAPIView.as_view()),

    path('profile/all/', ListAllProfileAPIView.as_view()),

    path('admin/', include(admin_router.urls)),
    # path('admin/profile/classroom/<int:classroom>/', ClassRoomProfileListAPIView.as_view()),
    # path('admin/profile/area/<int:area>/', AreaProfileListAPIView.as_view()),
    # path('admin/profile/region/<int:region>/', RegionProfileListAPIView.as_view()),
    # path('admin/profile/create/', ProfileCreateAPIView.as_view()),
    # path('admin/profile/edit/', ProfileEditAPIView.as_view()),

    path('admin/groups/', AdminGroupList.as_view())

    # path('create/', ProfileCreateAPIView.as_view(), name="user profile create"),
    # path('edit/<int:id>/', ProfileRetrieveUpdateDestroyAPIView.as_view(), name="user profile retrieve-update-delete"),
]
