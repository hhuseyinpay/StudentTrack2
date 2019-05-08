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
from .serializers import (UserModelSerializer, AdminMakeStudentSeriazlier, AdminChangeClassRoomSerializer,
                          AdminUserModelSerializer, UserListSerializer, UserModelSerializerV2,
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


class UserViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserModelSerializer
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = User.objects.all()

    @action(detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        user = self.request.user

        body = self.get_serializer(user).data
        return Response(data=body, status=status.HTTP_200_OK)


# **************************************************

"""
user lisetesi isteyince id ve name dönecek sadece !!!!
"""


class AdminUserViewSet(viewsets.ModelViewSet):
    serializer_class = AdminUserModelSerializer
    permission_classes = (IsAuthenticated, IsStaff, CanEditUser)
    queryset = User.objects.all()
    filter_fields = ('classroom',)

    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        else:
            return AdminUserModelSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, url_path='classroom/(?P<classroom_id>[0-9]+)', permission_classes=[IsAuthenticated, IsStaff])
    def classroom(self, request, classroom_id=None):
        qs = User.objects.filter(Q(classroom=classroom_id) | Q(classroom_teacher=classroom_id))

        body = UserListSerializer(qs, many=True).data
        return Response(data=body, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], permission_classes=[IsAuthenticated, IsStaff, CanEditUser])
    def makestudent(self, request, pk=None):
        staff = request.user
        user = self.get_object()
        serializer = AdminMakeStudentSeriazlier(data=request.data)
        serializer.is_valid(raise_exception=True)
        classroom = serializer.validated_data['classroom']

        error = False
        if staff.is_teacher() and not ClassRoom.objects.filter(id=classroom.id, teachers=staff).exists():
            error = True
        elif staff.is_executive() and not Area.objects.filter(id=classroom.area.id, executives=staff).exists():
            error = True
        elif staff.is_admin() and not Region.objects.filter(id=classroom.area.region.id, admins=staff).exists():
            error = True

        if error:
            body = {"classroom": "You have not authority on this classroom"}
            return Response(data=body, status=status.HTTP_400_BAD_REQUEST)

        user.classroom = classroom
        user.user_type = User.STUDENT
        user.save()

        # teacher veya executive'se sil.
        user.classroom_teacher.clear()
        user.area_executive.clear()
        # ClassRoom.objects.filter(teachers=user).delete()
        # Area.objects.filter(executives=user).delete()

        body = self.get_serializer(user).data
        return Response(data=body, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], permission_classes=[IsAuthenticated, IsExecutiveAdmin, CanEditUser])
    def maketeacher(self, request, pk=None):
        user = self.get_object()
        user.classroom = None
        user.user_type = User.TEACHER
        user.save()

        # executivese
        # Area.objects.filter(executives=user).delete()
        user.area_executive.clear()

        body = self.get_serializer(user).data
        return Response(data=body, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], permission_classes=[IsAuthenticated, IsAdmin, CanEditUser])
    def makeexecutive(self, request, pk=None):
        user = self.get_object()
        user.classroom = None
        user.user_type = User.EXECUTIVE
        user.save()

        # teachersa
        # ClassRoom.objects.filter(teachers=user).delete()
        user.classroom_teacher.clear()

        body = self.get_serializer(user).data
        return Response(data=body, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], permission_classes=[IsAuthenticated, IsStaff, CanEditUser])
    def changeclassroom(self, request, pk=None):
        staff = request.user
        user = self.get_object()
        seriazlier = AdminChangeClassRoomSerializer(data=request.data)
        seriazlier.is_valid(raise_exception=True)
        classroom = seriazlier.validated_data['classroom']

        if staff.is_executive() and not Area.objects.filter(id=classroom.area.id, executives=staff).exists() or \
                staff.is_admin() and not Area.objects.filter(id=classroom.area.id, region__admins=staff).exists():
            body = {"classroom": "You have not authority on this classroom"}
            return Response(data=body, status=status.HTTP_400_BAD_REQUEST)
        user.classroom = classroom

        user.save()

        body = self.get_serializer(user).data
        return Response(data=body, status=status.HTTP_200_OK)

    @action(detail=False, permission_classes=[IsAuthenticated, IsExecutiveAdmin])
    def getallmyuser(self, request):
        """
        burayı normalde get_queryset()'i override ederek yazacaktık ancak her api call'da bu filtrenin çalışacaktı.
        bunun önüne geçmek için yetkili olduğu userları çekebilmek için bu endpoint kullanılacak

        """
        staff = self.request.user
        users = User.objects.none()

        if staff.is_teacher():
            classrooms = ClassRoom.objects.filter(teachers=staff)
            users = User.objects.filter(classroom__in=classrooms)
        elif staff.is_executive():
            areas = Area.objects.filter(executives=staff).all()
            users = User.objects.filter(Q(classroom__area__in=areas) |
                                        Q(classroom_teacher__area__in=areas)).distinct()
        elif staff.is_admin():
            regions = Region.objects.filter(admins=staff)
            users = User.objects.filter(Q(classroom__area__region__in=regions) |
                                        Q(classroom_teacher__area__region__in=regions) |
                                        Q(area_executive__region__in=regions)).distinct()

        body = UserListSerializer(users, many=True).data
        return Response(data=body, status=status.HTTP_200_OK)


#########

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
    filter_fields = (
        'classroom', 'classroom__teachers', 'classroom__area__executives', 'classroom__area__region__admins'
    )

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
