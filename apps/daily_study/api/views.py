from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from account.api.permissions import IsStaff
from daily_study.filters import DailyStudyCreatedDayFilter
from daily_study.models import DailyStudy, Study
from .permissions import IsDailyStudyOwner, CanEditDailyStudy
from .serializer import DailyStudyModelSerializer, DailyStudyListSerializer, AdminDailyStudyModelSerializer

User = get_user_model()


class DailyStudyViewset(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, GenericViewSet):
    serializer_class = DailyStudyModelSerializer
    permission_classes = (IsAuthenticated, IsDailyStudyOwner)
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filter_class = DailyStudyCreatedDayFilter

    def get_queryset(self):
        return DailyStudy.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return DailyStudyListSerializer
        else:
            return DailyStudyModelSerializer

    @action(detail=False, permission_classes=[IsAuthenticated])
    def today(self, request):
        user = request.user
        if not user.has_group():
            body = {'detail': 'Herhangi bir çetele grubuna dahil değilsiniz!'}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)
        try:
            ds = DailyStudy.objects.get(user=user, created_day=now().date())
        except DailyStudy.DoesNotExist:
            ds = DailyStudy.objects.create(user=user, created_day=now().date())

            studies = []
            for course in user.course_group.courses.all():
                studies.append(Study(daily_study=ds, course=course, begining=0, end=0, amount=0))
            Study.objects.bulk_create(studies)

        body = self.get_serializer(ds).data
        return Response(body, status=status.HTTP_200_OK)


class AdminDailyStudyViewset(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, GenericViewSet):
    serializer_class = DailyStudyModelSerializer
    permission_classes = (IsAuthenticated, CanEditDailyStudy)
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filter_class = DailyStudyCreatedDayFilter
    queryset = DailyStudy.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return DailyStudyListSerializer
        else:
            return AdminDailyStudyModelSerializer

    @action(detail=False, url_path='today/user/(?P<user_id>[0-9]+)', permission_classes=[IsAuthenticated, IsStaff])
    def today(self, request, user_id=None):
        user = get_object_or_404(User, pk=user_id)
        if not user.has_group():
            body = {'detail': 'Herhangi bir çetele grubuna dahil değil!'}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)

        try:
            ds = DailyStudy.objects.get(user=user, created_day=now().date())
        except DailyStudy.DoesNotExist:
            ds = DailyStudy.objects.create(user=user, created_day=now().date())

            studies = []
            for course in user.course_group.courses.all():
                studies.append(Study(daily_study=ds, course=course, begining=0, end=0, amount=0))
            Study.objects.bulk_create(studies)

        body = self.get_serializer(ds).data
        return Response(body, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], permission_classes=[IsAuthenticated, CanEditDailyStudy])
    def validate(self, request, pk=None):
        ds = self.get_object()
        ds.is_validated = True
        ds.validator_user = request.user
        ds.validate_time = now()
        ds.save()

        body = self.get_serializer(ds).data
        return Response(body, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], permission_classes=[IsAuthenticated, CanEditDailyStudy])
    def invalidate(self, request, pk=None):
        ds = self.get_object()
        ds.is_validated = False
        ds.save()

        body = self.get_serializer(ds).data
        return Response(body, status=status.HTTP_200_OK)

    @action(detail=False, permission_classes=[IsAuthenticated, IsStaff])
    def total(self, request, *args, **kwargs):
        user = request.query_params.get('user', None)
        begining = request.query_params.get('begining', None)
        end = request.query_params.get('end', None)
        is_validated = request.query_params.get('is_validated', None)

        if not user or not begining or not end or not is_validated:
            body = {'detail': 'Onay durumu, talebe, başlangıç tarihi veya bitiş tarihi seçilmedi !!'}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)

        body = {
            "studies": [
            ]
        }

        queryset = self.filter_queryset(self.get_queryset())
        studies = Study.objects.filter(daily_study__in=queryset)
        user = get_object_or_404(User, pk=user)

        for course in user.course_group.courses.values_list('id', flat=True):
            b = {
                "course": course,
                "begining": 0,
                "end": 0,
                "amount": studies.filter(course=course).aggregate(total=Sum('amount'))['total'] or 0
            }

            body["studies"].append(b)
        # hangi sorguların yapıldığını kontrol etmek için:
        # from django.db import connection
        # print(connection.queries)

        return Response(body)
