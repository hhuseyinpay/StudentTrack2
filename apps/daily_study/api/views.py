from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from daily_study.models import DailyStudy
from daily_study.filters import DailyStudyCreatedDayFilter
from .permissions import IsDailyStudyOwner, CanEditDailyStudy
from .serializer import DailyStudyModelSerializer, DailyStudyListSerializer, AdminDailyStudyModelSerializer


class DailyStudyViewset(viewsets.ModelViewSet):
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

    def perform_create(self, serializer):
        if DailyStudy.objects.filter(user=self.request.user, created_day=now().date()).exists():
            raise ParseError("Bir günde birden fazla çetele oluşturulamaz.")

        serializer.save(user=self.request.user)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def today(self, request):
        ds = self.get_queryset().filter(created_day=now().date())
        if not ds:
            body = {"detail": "Bugün çetele oluşturulmadı."}
            return Response(data=body, status=status.HTTP_404_NOT_FOUND)
        body = self.get_serializer(ds, many=True).data
        return Response(body, status=status.HTTP_200_OK)


class AdminDailyStudyViewset(viewsets.ModelViewSet):
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

    @action(detail=True, permission_classes=[IsAuthenticated, CanEditDailyStudy])
    def validate(self, request, pk=None):
        ds = self.get_object()
        ds.is_validated = True
        ds.validator_user = request.user
        ds.validate_time = now()
        ds.save()

        body = self.get_serializer(ds, many=True).data
        return Response(body, status=status.HTTP_200_OK)

    @action(detail=True, permission_classes=[IsAuthenticated, CanEditDailyStudy])
    def invalidate(self, request, pk=None):
        ds = self.get_object()
        ds.is_validated = False
        ds.save()

        body = self.get_serializer(ds, many=True).data
        return Response(body, status=status.HTTP_200_OK)
