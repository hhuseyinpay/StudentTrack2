from django.contrib.auth.models import User
from rest_framework import generics, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny

from accounts.api.permissions import IsAdmin, IsTeacherExecutiveAdmin
from base.models import Course, Groups
from .serializer import GroupCourseModelSerializer, GroupSerializer


class GroupViewset(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    queryset = Groups.objects.filter()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdmin]
        else:
            # which is permissions.AllowAny
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class UserGroupCourseListAPIView(generics.ListAPIView):
    serializer_class = GroupCourseModelSerializer

    def get_queryset(self):

        try:
            user = User.objects.get(id=self.kwargs['user'])
        except User.DoesNotExist:
            # raise NotFound("User not found")
            raise NotFound("Kullanıcı bulunamadı")

        group = user.profile.group
        if group:
            return group.courses.all()
        return Course.objects.none()


class GroupListAPIView(generics.ListAPIView):
    serializer_class = GroupSerializer
    queryset = Groups.objects.all()
