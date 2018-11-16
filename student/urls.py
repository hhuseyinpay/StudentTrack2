"""student URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include
from django.urls import path
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter

from account.api.views import UserViewSet, UserLoginAPIView, AdminUserViewSet
from course.api.views import CourseGroupViewset, CourseViewSet
from daily_study.api.views import DailyStudyViewset, AdminDailyStudyViewset
from location.api.views import ClassRoomRetrieveViewSet, AreaRetrieveViewSet, AdminClassroomViewSet, AdminAreaViewset
from syllabus.api.views import SyllabusViewSet, UserSyllabusViewSet, AdminUserSyllabusViewSet, ContentViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.IsAuthenticated,),
)
admin_router = DefaultRouter()
user_router = DefaultRouter()

###
# account app
###
user_router.register('user', UserViewSet, 'user-viewset')

admin_router.register('user', AdminUserViewSet, 'adminuser-viewset')

###
# location app
###
user_router.register('classroom', ClassRoomRetrieveViewSet, 'classroomretrieve-viewset')
user_router.register('area', AreaRetrieveViewSet, 'arearetrieve-viewset')
user_router.register('region', ClassRoomRetrieveViewSet, 'regionretrieve-viewset')

admin_router.register('classroom', AdminClassroomViewSet, 'adminclassroom-viewset')
admin_router.register('area', AdminAreaViewset, 'adminarea-viewset')

###
# course app
###
user_router.register('course-group', CourseGroupViewset, 'coursegroup-viewset')
user_router.register('course', CourseViewSet, 'course-viewset')

###
# syllabus app
###
user_router.register('content', ContentViewSet, 'content-viewset')
user_router.register('syllabus', SyllabusViewSet, 'syllabus-viewset')
user_router.register('user-syllabus', UserSyllabusViewSet, 'usersyllabus-viewset')

admin_router.register('user-syllabus', AdminUserSyllabusViewSet, 'adminusersyllabus-viewset')

###
# daily_study app
###
user_router.register('daily-study', DailyStudyViewset, 'dailystudy-viewset')

admin_router.register('daily-study', AdminDailyStudyViewset, 'admindailystudy-viewset')

urlpatterns = [
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('admin/', admin.site.urls),

    path('api/', include(user_router.urls)),
    path('api/admin/', include(admin_router.urls)),
    path('api/login', UserLoginAPIView.as_view(), name='api-login')

    # path('reports/', include('reports.urls')),
    # path('api/reports/', include('reports.api.urls'))
]

if settings.DEBUG:
    urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]
