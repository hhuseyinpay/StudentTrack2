from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from student.account.permissions import IsStaff, IsExecutiveAdmin

from student.location.models import ClassRoom
from .permissions import CanEditClassroom
from .serializers import (ClassRoomListSerializer, ClassRoomModelSerializer)

User = get_user_model()


# **************************************************

class AdminClassroomViewSet(viewsets.GenericViewSet):
    serializer_class = ClassRoomModelSerializer
    permission_classes = (IsAuthenticated, IsExecutiveAdmin, CanEditClassroom)
    queryset = ClassRoom.objects.all()

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
