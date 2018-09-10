from django.urls import path

# from rest_framework.routers import DefaultRouter

from .views import DSListCreateAPIView, DSRetrieveUpdateAPIView, DSIntervalListAPIView, \
    GroupCourseListAPIView, AdminDSRetrieveUpdateAPIView, AdminDSValidateAPIView, AdminDSClassroomListAPIView

# router = DefaultRouter()
# router.register('ceteles', CeteleViewSet, base_name="ceteles")

urlpatterns = [
    path('courses/', GroupCourseListAPIView.as_view()),

    # api/daily_study/
    path('me/', DSListCreateAPIView.as_view(), name="user-daily_study-list-create"),

    # api/daily_study/x/
    path('me/<int:id>/', DSRetrieveUpdateAPIView.as_view(), name="user-daily_study-retrieve-update"),

    path('me/begining/<str:begining>/end/<str:end>/', DSIntervalListAPIView.as_view(),
         name="user daily_study interval list"),

    # url('viewset/', include(router.urls)),
    path('admin/validate/<int:id>/', AdminDSValidateAPIView.as_view(), name="admin daily_study validate"),
    path('admin/edit/<int:id>/', AdminDSRetrieveUpdateAPIView.as_view(),
         name="admin daily_study retrieve update destroy"),
    path('admin/classroom/<int:classroom>/day/<str:day>/', AdminDSClassroomListAPIView.as_view()),

]
