from django.contrib.auth.models import User
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from daily_study.models import DailyStudy, Study, Course
from .serializer import DailyStudyModelSerializer, GroupCourseModelSerializer, DailyStudyValidateSerializer
from .permissions import IsTeExAd, CanEditDailyStudy


class DSListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DailyStudyModelSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return DailyStudy.objects.get_day(self.request.user)

    def get_serializer_context(self):
        return {'user': self.request.user}


class DSRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = DailyStudyModelSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    lookup_field = 'id'

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_queryset(self):
        # sadece userın editleyebileceklerini döndürüyor.
        return DailyStudy.objects.user_editables(self.request.user)


class DSIntervalListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = DailyStudyModelSerializer

    def get_queryset(self):
        user = self.request.user
        begining = self.kwargs['begining']
        end = self.kwargs['end']

        return DailyStudy.objects.get_by_interval(user=user, begining=begining, end=end)


class GroupCourseListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = GroupCourseModelSerializer

    def get_queryset(self):
        group = self.request.user.profile.group
        if group:
            return group.courses.all()
        return Course.objects.none()


class AdminDSRetrieveUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DailyStudyModelSerializer
    permission_classes = (IsAuthenticated, CanEditDailyStudy,)
    authentication_classes = (TokenAuthentication,)
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


class AdminDSClassroomListAPIView(generics.ListAPIView):
    serializer_class = DailyStudyModelSerializer
    permission_classes = (IsAuthenticated, IsTeExAd,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        user = self.request.user
        classroom = self.kwargs['classroom']
        day = self.kwargs['day']
        users = User.objects.filter(profile__classroom=classroom)
        return DailyStudy.objects.filter(user__in=users, created_day=day)


class AdminDsRetrieveUserDayAPIView(generics.RetrieveAPIView):
    serializer_class = DailyStudyModelSerializer
    permission_classes = (IsAuthenticated, CanEditDailyStudy,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        user = self.kwargs['classroom']
        day = self.kwargs['day']
        return DailyStudy.objects.filter(user=user, created_day=day)
