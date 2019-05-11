from django.conf import settings
from django.conf.urls import url
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import SimpleRouter

from .report.views import DailyStudyReport
from .daily_study.views import DailyStudyViewset, AdminDailyStudyViewset
from .syllabus.views import ContentViewSet, SyllabusViewSet, AdminUserSyllabusViewSet
from .course.views import CourseGroupViewset, CourseViewSet
from .location.views import AdminClassroomViewSet

from .account.views import UserViewSet, AdminUserViewSet, UserLoginAPIView, Kayit

admin_router = SimpleRouter()
user_router = SimpleRouter()

###
# account app
###
user_router.register('user', UserViewSet, 'user-viewset')

admin_router.register('user', AdminUserViewSet, 'adminuser-viewset')

###
# location app
###
admin_router.register('classroom', AdminClassroomViewSet, 'adminclassroom-viewset')

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

admin_router.register('user-syllabus', AdminUserSyllabusViewSet, 'adminusersyllabus-viewset')

###
# daily_study app
###
user_router.register('daily-study', DailyStudyViewset, 'dailystudy-viewset')

admin_router.register('daily-study', AdminDailyStudyViewset, 'admindailystudy-viewset')

###
# report
###

report_router = SimpleRouter()
report_router.register('daily-study', DailyStudyReport, 'report-dailystudy')

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include(user_router.urls)),
    path('api/admin/', include(admin_router.urls)),
    path('api/report/', include(report_router.urls)),

    path('api/login', UserLoginAPIView.as_view(), name='api-login'),
    path('api/kayit', Kayit.as_view())
]

urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    # validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns += (url(r'^api/swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),)
