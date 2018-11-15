from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from account.models import User
from course.models import CourseGroups, Course
from .serializer import CourseGroupModelSerializer, CourseGroupListSerializer, CourseModelSerializer


class CourseGroupViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = CourseGroupModelSerializer
    queryset = CourseGroups.objects.filter()

    def get_serializer_class(self):
        if self.action == 'list':
            return CourseGroupListSerializer
        return self.serializer_class

    @action(detail=False, url_path='user/(?P<user>[0-9]+)')
    def user(self, request, user=None):
        try:
            user = User.objects.get(id=user)
        except User.DoesNotExist:
            # raise NotFound("User not found")
            raise NotFound("Kullanıcı bulunamadı")
        course_group = user.course_group

        body = self.get_serializer(course_group).data
        return Response(data=body, status=status.HTTP_200_OK)


class CourseViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CourseModelSerializer
    queryset = Course.objects.all()
