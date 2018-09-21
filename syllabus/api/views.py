from django.contrib.auth.models import Group
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from ..models import Syllabus, UserSyllabus
from .serializer import SyllabusModelSerializer, UserSyllabusModelSerializer, SyllabusListSerializer, \
    UserSyllabusListSerializer, UserSyllabusValidateSerializer, AdminUserSyllabusModelSerializer
from .permissions import CanEditSyllabus


class SyllabusAllListAPIView(generics.ListAPIView):
    serializer_class = SyllabusModelSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return Syllabus.objects.all()


class SyllabusLevelListAPIView(generics.ListAPIView):
    serializer_class = SyllabusListSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        lvl = self.kwargs['level']
        return Syllabus.objects.level(lvl)


class SyllabusLevelCourseAPIView(generics.ListAPIView):
    serializer_class = SyllabusModelSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        lvl = self.kwargs['level']
        cr = self.kwargs['course']
        return Syllabus.objects.level_course(lvl, cr)


# class UserSyllabusListCreateAPIView(generics.ListCreateAPIView):
#     serializer_class = UserSyllabusModelSerializer
#
#     def get_queryset(self):
#         return UserSyllabus.objects.user(self.request.user)
#
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)


class UserSyllabusUserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSyllabusModelSerializer
    http_method_names = ['post', 'delete']

    def get_queryset(self):
        return UserSyllabus.objects.user(self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserSyllabusAPIView(generics.ListAPIView):
    serializer_class = UserSyllabusModelSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        lvl = self.kwargs['level']
        cr = self.kwargs['course']

        return UserSyllabus.objects.filter(user=self.request.user, content__syllabus__course=cr,
                                           content__syllabus__level=lvl)

    def get_serializer_context(self):
        return {'user': self.request.user}


class AdminUSAPIView(generics.ListAPIView):
    serializer_class = AdminUserSyllabusModelSerializer
    permission_classes = (IsAuthenticated, CanEditSyllabus)

    def get_queryset(self):
        user = self.kwargs['user']
        lvl = self.kwargs['level']
        cr = self.kwargs['course']

        return UserSyllabus.objects.filter(user=user, content__syllabus__course=cr,
                                           content__syllabus__level=lvl)

    def get_serializer_context(self):
        return {'user': self.kwargs['user']}


class AdminUSValidateAPIView(generics.UpdateAPIView):
    serializer_class = UserSyllabusValidateSerializer
    permission_classes = (IsAuthenticated, CanEditSyllabus)
    queryset = UserSyllabus.objects.all()
    lookup_field = 'id'

    def get_serializer_context(self):
        return {'user': self.request.user}


class AdminUSNotValidatedAPIView(generics.ListAPIView):
    serializer_class = UserSyllabusModelSerializer
    permission_classes = (IsAuthenticated, CanEditSyllabus)

    def get_queryset(self):
        user = self.kwargs['user']
        return UserSyllabus.objects.filter(user=user, is_validated=False)

    def get_serializer_context(self):
        return {'user': self.request.user}
