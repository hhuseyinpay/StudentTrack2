from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django.shortcuts import get_object_or_404

from account.api.permissions import IsStaff
from daily_study.models import DailyStudy, Study
from daily_study.filters import DailyStudyCreatedDayFilter
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
        ds = self.get_queryset().filter(created_day=now().date())
        # bugün çetele doldurulmadıysa otomatik olarak boş bir çelete oluştur..
        if not ds:
            ds = DailyStudy.objects.create(user=user, created_day=now().date())

            studies = []
            for course in user.course_group.courses.all():
                studies.append(Study(daily_study=ds, course=course, begining=0, end=0, amount=0))
            Study.objects.bulk_create(studies)
            body = self.get_serializer(ds).data
        else:
            body = self.get_serializer(ds, many=True).data
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
        ds = self.get_queryset().filter(user=user_id, created_day=now().date())
        # bugün çetele doldurulmadıysa otomatik olarak boş bir çelete oluştur..
        if not ds:
            user = get_object_or_404(User.objects.all(), pk=user_id)
            ds = DailyStudy.objects.create(user=user_id, created_day=now().date())

            studies = []
            for course in user.course_group.courses.all():
                studies.append(Study(daily_study=ds, course=course, begining=0, end=0, amount=0))
            Study.objects.bulk_create(studies)
            body = self.get_serializer(ds).data
        else:
            body = self.get_serializer(ds, many=True).data
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
