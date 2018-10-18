from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated

from base.models import Course, Groups
from .serializer import GroupCourseModelSerializer, GroupSerializer


class UserGroupCourseListAPIView(generics.ListAPIView):
    serializer_class = GroupCourseModelSerializer
    permission_classes = (IsAuthenticated,)

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
    # permission_classes = (IsAuthenticated, IsTeExAd)
    queryset = Groups.objects.all()
