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

    @action(detail=False, url_path='user/(?P<user_id>[0-9]+)')
    def user(self, request, user_id=None):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            # raise NotFound("User not found")
            raise NotFound("Kullanıcı bulunamadı")
        course_group = user.course_group

        body = self.get_serializer(course_group).data
        return Response(data=body, status=status.HTTP_200_OK)

    @action(detail=False)
    def mycourses(self, request):
        user = self.request.user
        if not user.has_group():
            qs = user.course_group.courses.all()
        else:
            body = {"detail": "Çetele grubu bulunamadı."}
            return Response(data=body, status=status.HTTP_404_NOT_FOUND)

        body = CourseModelSerializer(qs, many=True).data
        return Response(data=body, status=status.HTTP_200_OK)


class CourseViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CourseModelSerializer
    queryset = Course.objects.all()
