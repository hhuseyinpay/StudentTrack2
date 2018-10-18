from django.contrib.auth.models import User

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotFound

from apps.daily_study.models import DailyStudy
from .serializer import DailyStudyModelSerializer, DailyStudyValidateSerializer
from .permissions import IsTeacherExecutiveAdmin, CanEditDailyStudy, is_authority


class DSListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DailyStudyModelSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return DailyStudy.objects.get_day(self.request.user)

    def get_serializer_context(self):
        return {'user': self.request.user}


class DSRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = DailyStudyModelSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'id'

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_queryset(self):
        # sadece userın editleyebileceklerini döndürüyor.
        return DailyStudy.objects.user_editables(self.request.user)


class DSIntervalListAPIView(generics.ListAPIView):
    serializer_class = DailyStudyModelSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        begining = self.kwargs['begining']
        end = self.kwargs['end']

        return DailyStudy.objects.get_by_interval(user=user, begining=begining, end=end)


class AdminDSRetrieveUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DailyStudyModelSerializer
    permission_classes = (IsAuthenticated, CanEditDailyStudy,)
    queryset = DailyStudy.objects.all()
    lookup_field = 'id'

    def get_serializer_context(self):
        return {'user': self.request.user}


class AdminDSValidateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = DailyStudyValidateSerializer
    permission_classes = (IsAuthenticated, CanEditDailyStudy,)
    queryset = DailyStudy.objects.all()
    lookup_field = 'id'

    def get_serializer_context(self):
        return {'user': self.request.user}


class AdminDSNotvalidatedAPIView(generics.ListAPIView):
    serializer_class = DailyStudyModelSerializer
    permission_classes = (IsAuthenticated, IsTeacherExecutiveAdmin,)

    def get_queryset(self):
        try:
            user = User.objects.get(id=self.kwargs['user'])
        except User.DoesNotExist:
            # raise NotFound("User not found")
            raise NotFound("Kullanıcı bulunamadı")
        if not is_authority(self.request.user, user.profile):
            raise PermissionDenied()
        return DailyStudy.objects.filter(user=user, is_validated=False).order_by("-created_day")


class AdminDSClassroomListAPIView(generics.ListAPIView):
    serializer_class = DailyStudyModelSerializer
    permission_classes = (IsAuthenticated, IsTeacherExecutiveAdmin,)

    def get_queryset(self):
        user = self.request.user
        classroom = self.kwargs['classroom']
        day = self.kwargs['day']
        users = User.objects.filter(profile__classroom=classroom)
        return DailyStudy.objects.filter(user__in=users, created_day=day)


class AdminDsRetrieveUserDayAPIView(generics.RetrieveAPIView):
    serializer_class = DailyStudyModelSerializer
    permission_classes = (IsAuthenticated, CanEditDailyStudy)
    lookup_field = "user"

    def get_queryset(self):
        user = self.kwargs['user']
        day = self.kwargs['day']
        return DailyStudy.objects.filter(user=user, created_day=day)


class AdminDSIntervalListAPIView(generics.ListAPIView):
    serializer_class = DailyStudyModelSerializer
    permission_classes = (IsAuthenticated, IsTeacherExecutiveAdmin)

    def get_queryset(self):
        try:
            user = User.objects.get(id=self.kwargs['user'])
        except User.DoesNotExist:
            # raise NotFound("User not found")
            raise NotFound("Kullanıcı bulunamadı")
        if not is_authority(self.request.user, user.profile):
            raise PermissionDenied()

        begining = self.kwargs['begining']
        end = self.kwargs['end']

        return DailyStudy.objects.get_by_interval(user=user, begining=begining, end=end)
