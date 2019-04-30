from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins, status
from rest_framework.authtoken import views
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from student.account.models import User
from student.location.models import ClassRoom, Area, Region
from .permissions import IsStaff, IsExecutiveAdmin, IsAdmin, CanEditUser, IsOwner, CanEditUserV2, IsStaffV2, \
    IsExecutiveAdminV2, IsAdminV2
from .serializers import (UserModelSerializerV2,
                          AdminUserModelSerializerV2, AdminStudentSerializer, AdminTeacherSerializer,
                          AdminExecutiveSerializer, PasswordChangeSerializer)


class UserLoginAPIView(views.ObtainAuthToken):
    serializer_class = views.AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        if not serializer.is_valid():
            return Response({'detail': "Kullanıcı adı veya Parola yanlış"},
                            status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'user': user.id, 'token': token.key})


# **************************************************


class Kayit(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        return Response()


#########

class UserViewSetV2(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserModelSerializerV2
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = User.objects.all()

    @action(detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        user = self.request.user

        body = self.get_serializer(user).data
        return Response(data=body)

    @swagger_auto_schema(request_body=PasswordChangeSerializer)
    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def changepassword(self, request):
        user = request.user
        serializer = PasswordChangeSerializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response()


class AdminUserViewSetV2(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = AdminUserModelSerializerV2
    permission_classes = (CanEditUserV2,)
    queryset = User.objects.all()
    filter_fields = ('classroom', 'classroom__teachers')

    @staticmethod
    def _classroom_permission_check(staff, classroom):
        classroom_error_message = "Bu classroomda yetkili değilsin"
        if staff.is_teacher() and not classroom.teachers.filter(pk=staff.id).exists():
            raise PermissionDenied(classroom_error_message)
        elif staff.is_executive() and not classroom.area.executives.filter(pk=staff.id).exists():
            raise PermissionDenied(classroom_error_message)
        elif staff.is_admin() and not classroom.area.region.admins.filter(pk=staff.id).exists():
            raise PermissionDenied(classroom_error_message)

    @swagger_auto_schema(request_body=AdminStudentSerializer)
    @action(detail=False, methods=['post'], permission_classes=[IsStaffV2])
    def createstudent(self, request):
        serializer = AdminStudentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        staff = request.user
        self._classroom_permission_check(staff, serializer.validated_data['classroom'])
        serializer.validated_data['user_type'] = 8
        user = User.objects.create_user(**serializer.validated_data)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=AdminTeacherSerializer)
    @action(detail=False, methods=['post'], permission_classes=[IsExecutiveAdminV2])
    def createteacher(self, request):
        serializer = AdminTeacherSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        staff = request.user
        classroom = serializer.validated_data.pop('assigned_classroom_id')
        self._classroom_permission_check(staff, classroom)

        serializer.validated_data['user_type'] = 4
        user = User.objects.create_user(**serializer.validated_data)
        classroom.teachers.add(user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=AdminExecutiveSerializer)
    @action(detail=False, methods=['post'], permission_classes=[IsAdminV2])
    def createexecutive(self, request):
        serializer = AdminExecutiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        staff = request.user
        area = serializer.validated_data.pop('assigned_area_id')
        if not area.region.admins.filter(pk=staff.id).exists():
            raise PermissionDenied("Bu bölgede yetkili değilisiniz!")

        serializer.validated_data['user_type'] = 2
        user = User.objects.create_user(**serializer.validated_data)
        area.executives.add(user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=PasswordChangeSerializer)
    @action(detail=True, methods=['put'], permission_classes=[CanEditUserV2])
    def changepassword(self, request):
        user = self.get_object()
        serializer = PasswordChangeSerializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response()
