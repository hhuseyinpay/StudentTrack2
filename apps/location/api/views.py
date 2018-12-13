from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from account.api.permissions import IsStaff, IsExecutiveAdmin
from account.api.serializer import UserModelSerializer
from location.models import ClassRoom, Area, Region
from .permissions import CanEditClassroom, CanEditArea
from .serializer import (ClassRoomListSerializer, AreaListSerializer,
                         ClassRoomModelSerializer, AreaModelSerializer, RegionModelSerializer,
                         AdminAreaExcutiveSerializer, AdminClassroomTeacherSerializer)

User = get_user_model()


class ClassRoomRetrieveViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ClassRoomModelSerializer
    queryset = ClassRoom.objects.all()


class AreaRetrieveViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = AreaModelSerializer
    queryset = Area.objects.all()


class RegionRetrieveViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = RegionModelSerializer
    queryset = Region.objects.all()


# **************************************************

class AdminClassroomViewSet(viewsets.ModelViewSet):
    serializer_class = ClassRoomModelSerializer
    permission_classes = (IsAuthenticated, IsExecutiveAdmin, CanEditClassroom)
    queryset = ClassRoom.objects.all()

    #
    # def get_queryset(self):
    #     if self.request.user.profile.is_executive:
    #         return ClassRoom.objects.filter(area__executives=self.request.user)
    #     else:
    #         return ClassRoom.objects.filter(area__region__admins=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return ClassRoomListSerializer
        else:
            return ClassRoomModelSerializer

    @action(detail=False, permission_classes=[IsAuthenticated, IsStaff])
    def myclassrooms(self, request):
        staff = request.user
        if staff.is_teacher():
            classrooms = ClassRoom.objects.filter(teachers=request.user)
        elif staff.is_executive():
            classrooms = ClassRoom.objects.filter(area__executives=staff)
        else:
            classrooms = ClassRoom.objects.filter(area__region__admins=staff)

        body = ClassRoomListSerializer(classrooms, many=True).data
        return Response(body, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def teachers(self, request, pk=None):
        classroom = self.get_object()
        teachers = classroom.teachers.all()

        body = UserModelSerializer(teachers, many=True).data
        return Response(data=body, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], permission_classes=[IsAuthenticated, CanEditClassroom])
    def addteacher(self, request, pk=None):
        classroom = self.get_object()
        serializer = AdminClassroomTeacherSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        classroom.teachers.add(user)
        classroom.save()

        body = self.get_serializer(classroom).data
        return Response(data=body, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['put'], permission_classes=[IsAuthenticated, CanEditClassroom])
    def removeteacher(self, request, pk=None):
        classroom = self.get_object()
        serializer = AdminClassroomTeacherSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        classroom.teachers.filter(id=user.id).delete()
        classroom.save()

        body = self.get_serializer(self.get_object()).data
        return Response(data=body, status=status.HTTP_202_ACCEPTED)


class AdminAreaViewset(viewsets.ModelViewSet):
    serializer_class = AreaModelSerializer
    permission_classes = (IsAuthenticated, IsExecutiveAdmin, CanEditArea)
    queryset = Area.objects.all()

    #
    # def get_queryset(self):
    #     if self.request.user.profile.is_executive:
    #         return Area.objects.filter(executives=self.request.user)
    #     else:
    #         region = Region.objects.filter(admins=self.request.user)
    #         return Area.objects.filter(region__in=region)

    def get_serializer_class(self):
        if self.action == 'list':
            return AreaListSerializer
        return self.serializer_class

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsExecutiveAdmin])
    def myareas(self, request):
        staff = request.user
        if staff.is_executive():
            areas = Area.objects.filter(executives=staff)
        else:
            areas = Area.objects.filter(region__admins=staff)

        body = AreaListSerializer(areas, many=True).data
        return Response(body, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def executives(self, request, pk=None):
        area = self.get_object()
        executives = area.executives.all()

        body = UserModelSerializer(executives, many=True).data
        return Response(data=body, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def teachers(self, request, pk=None):
        area = self.get_object()
        teachers = User.objects.filter(classroom_teacher__area=area)

        body = UserModelSerializer(teachers, many=True).data
        return Response(data=body, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], permission_classes=[IsAuthenticated, IsExecutiveAdmin])
    def addexecutive(self, request, pk=None):
        area = self.get_object()
        serializer = AdminAreaExcutiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        area.executives.add(user)
        area.save()

        body = self.get_serializer(self.get_object()).data
        return Response(data=body, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], permission_classes=[IsAuthenticated, IsExecutiveAdmin])
    def removeexecutive(self, request, pk=None):
        area = self.get_object()
        serializer = AdminAreaExcutiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        area.executives.filter(id=user.id).delete()
        area.save()

        body = self.get_serializer(self.get_object()).data
        return Response(data=body, status=status.HTTP_200_OK)


class AdminRegionViewset(viewsets.GenericViewSet):
    serializer_class = RegionModelSerializer
    permission_classes = (IsAuthenticated, IsExecutiveAdmin, CanEditArea)
    queryset = Region.objects.all()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsExecutiveAdmin])
    def myregion(self, request):
        staff = request.user
        if staff.is_executive():
            region = Region.objects.filter(area__executives=staff).first()
        else:
            region = Region.objects.filter(admins=staff).first()

        body = AreaListSerializer(region).data
        return Response(body, status=status.HTTP_200_OK)
