from django.conf import settings
from django.conf.urls import url
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import SimpleRouter

from .daily_study.views import DailyStudyViewset, AdminDailyStudyViewset, AdminDailyStudyViewsetV2
from .syllabus.views import ContentViewSet, SyllabusViewSet, UserSyllabusViewSet, AdminUserSyllabusViewSet, \
    UserSyllabusViewSetV2, AdminUserSyllabusViewSetV2
from .course.views import CourseGroupViewset, CourseViewSet
from .location.views import ClassRoomRetrieveViewSet, AreaRetrieveViewSet, RegionRetrieveViewSet, AdminClassroomViewSet, \
    AdminAreaViewset, AdminRegionViewset
from .account.views import UserViewSet, AdminUserViewSet, UserLoginAPIView, Kayit, UserViewSetV2, AdminUserViewSetV2

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
user_router.register('classroom', ClassRoomRetrieveViewSet, 'classroomretrieve-viewset')
user_router.register('area', AreaRetrieveViewSet, 'arearetrieve-viewset')
user_router.register('region', RegionRetrieveViewSet, 'regionretrieve-viewset')

admin_router.register('classroom', AdminClassroomViewSet, 'adminclassroom-viewset')
admin_router.register('area', AdminAreaViewset, 'adminarea-viewset')
admin_router.register('region', AdminRegionViewset, 'adminregion-viewset')
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
########################

###
# V2
###
user_routerV2 = SimpleRouter()
admin_routerV2 = SimpleRouter()
user_routerV2.register('user', UserViewSetV2, 'user-viewset-V2')
admin_routerV2.register('user', AdminUserViewSetV2, 'adminuser-viewset-V2')

user_routerV2.register('user-syllabus', UserSyllabusViewSetV2, 'user-syllabus-viewset-V2')
admin_routerV2.register('user-syllabus', AdminUserSyllabusViewSetV2,'adminusersyllabus-viewset-V2' )

admin_routerV2.register('daily-study', AdminDailyStudyViewsetV2, 'admindailystudy-viewset-V2')
########################
###
# report
###

urlpatterns = [
# name space eklenebilmesi için lego'ya bak. api appi oluşturmuş içine v1 dosyasını koymuş oradan include ediyor..

    path('admin/', admin.site.urls),

    path('api/v2/', include(user_routerV2.urls)),
    path('api/v2/admin/', include(admin_routerV2.urls)),

    path('api/', include(user_router.urls)),
    path('api/admin/', include(admin_router.urls)),

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
