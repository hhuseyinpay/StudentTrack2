from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AdminClassroomViewSet, AdminAreaViewset, ClassRoomRetrieveViewSet

user_router = DefaultRouter()

admin_router = DefaultRouter()

admin_router.register('classroom', AdminClassroomViewSet, 'admin_classroomviewset')
admin_router.register('area', AdminAreaViewset, 'admin-areaviewset')

urlpatterns = [
    path('admin/', include(admin_router.urls)),

    path('classroom/<int:pk>/', ClassRoomRetrieveViewSet.as_view())
]
