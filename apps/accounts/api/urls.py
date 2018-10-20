from django.urls import path, include
from rest_framework.routers import DefaultRouter

from accounts.api.views import ProfileViewSet, ListAllProfileAPIView, UserLoginAPIView, \
    AdminProfileViewSet, AdminClassroomViewSet, AdminAreaViewset, ClassRoomRetrieveAPIView

user_router = DefaultRouter()
user_router.register('', ProfileViewSet, 'profileviewset')

admin_router = DefaultRouter()
admin_router.register('profile', AdminProfileViewSet, 'admin_profile_viewset')

admin_router.register('classroom', AdminClassroomViewSet, 'admin_classroomviewset')
admin_router.register('area', AdminAreaViewset, 'admin-areaviewset')

urlpatterns = [
    path('profile/', include(user_router.urls)),
    path('login/', UserLoginAPIView.as_view()),

    path('profile/all/', ListAllProfileAPIView.as_view()),

    path('admin/', include(admin_router.urls)),

    path('classroom/<int:pk>/', ClassRoomRetrieveAPIView.as_view())
]
