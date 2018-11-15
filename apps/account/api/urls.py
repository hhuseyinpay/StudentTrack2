from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, UserLoginAPIView, AdminUserViewSet

user_router = DefaultRouter()
user_router.register('', UserViewSet, 'profileviewset')

admin_router = DefaultRouter()
admin_router.register('profile', AdminUserViewSet, 'admin_profile_viewset')

urlpatterns = [
    path('profile/', include(user_router.urls)),
    path('login/', UserLoginAPIView.as_view()),

    path('admin/', include(admin_router.urls)),
]
