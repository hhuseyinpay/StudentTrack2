from django.urls import path

# from rest_framework.routers import DefaultRouter

from .views import DSListCreateAPIView, DSRetrieveUpdateAPIView, DSIntervalListAPIView, \
    AdminDSRetrieveUpdateAPIView, AdminDSValidateAPIView, AdminDSClassroomListAPIView, \
    AdminDsRetrieveUserDayAPIView, AdminDSIntervalListAPIView, AdminDSNotvalidatedAPIView

# router = DefaultRouter()
# router.register('ceteles', CeteleViewSet, base_name="ceteles")

urlpatterns = [
    # api/daily_study/
    path('me/', DSListCreateAPIView.as_view(), name="user-daily_study-list-create"),

    # api/daily_study/x/
    path('me/<int:id>/', DSRetrieveUpdateAPIView.as_view(), name="user-daily_study-retrieve-update"),

    path('me/begining/<str:begining>/end/<str:end>/', DSIntervalListAPIView.as_view(),
         name="user daily_study interval list"),

    # url('viewset/', include(router.urls)),
    path('admin/notvalidated/user/<int:user>/', AdminDSNotvalidatedAPIView.as_view()),
    path('admin/validate/<int:id>/', AdminDSValidateAPIView.as_view(), name="admin daily_study validate"),
    path('admin/edit/<int:id>/', AdminDSRetrieveUpdateAPIView.as_view(), ),
    path('admin/user/<int:user>/day/<str:day>/', AdminDsRetrieveUserDayAPIView.as_view()),
    path('admin/user/<int:user>/begining/<str:begining>/end/<str:end>/', AdminDSIntervalListAPIView.as_view()),
    path('admin/classroom/<int:classroom>/day/<str:day>/', AdminDSClassroomListAPIView.as_view()),

]