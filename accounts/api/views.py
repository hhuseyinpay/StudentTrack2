from django.db.models import Q
from rest_framework import generics, viewsets, mixins, status
from rest_framework.authtoken import views
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User, Profile, ClassRoom, Groups, Area, Region
from .permissions import IsTeacherExecutiveAdmin, IsExecutiveAdmin, IsAdmin, CanEditClassroom, CanEditProfile
from .serializer import (
    ProfileModelSerializer, ClassRoomModelSerializer,
    AdminProfileSerializer, AdminMakeStudentSeriazlier,
    AdminChangeClassRoomSerializer, AdminChangeAreaSerializer,
    AdminClassroomTeacherSerializer, AdminClassroomSerializer, AdminAreaSeriazlier,
    AdminAreaExcutiveSerializer, AreaModelSerializer, MyClassRoomSerializer, MyAreaSerializer, StudentProfileSerializer)


class UserLoginAPIView(views.ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'user': user.id, 'token': token.key})


class ListAllProfileAPIView(generics.ListAPIView):
    serializer_class = ProfileModelSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Profile.objects.all()


class ProfileViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = StudentProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Profile.objects.filter(id=self.request.user.profile.id)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        qs = self.get_queryset()

        body = self.get_serializer(qs.first()).data
        return Response(data=body, status=status.HTTP_200_OK)


class ClassRoomRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = ClassRoomModelSerializer
    queryset = ClassRoom.objects.all()


# **************************************************


class AdminProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileModelSerializer
    permission_classes = (IsAuthenticated, CanEditProfile)
    queryset = Profile.objects.all()
    filter_fields = ('is_student', 'is_teacher', 'is_executive', 'classroom')

    def create(self, request, *args, **kwargs):
        serializer = AdminProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(created_by=request.user, is_student=True)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = AdminProfileSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        body = self.get_serializer(instance).data
        return Response(data=body, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['put'], permission_classes=[IsTeacherExecutiveAdmin])
    def makestudent(self, request, pk=None):
        profile = self.get_object()
        serializer = AdminMakeStudentSeriazlier(data=request.data)
        serializer.is_valid(raise_exception=True)
        classroom = serializer.validated_data['classroom']
        group = serializer.validated_data['group']

        # optimize edilebilir?
        if classroom not in ClassRoom.objects.filter(teachers=request.user) and \
                classroom.area not in Area.objects.filter(executives=request.user) and \
                classroom.area.region not in Region.objects.filter(admins=request.user):
            body = {"classroom": "You have not authority on this classroom"}
            return Response(data=body, status=status.HTTP_400_BAD_REQUEST)

        profile.group = group
        profile.classroom = classroom
        profile.is_student = True
        profile.is_teacher = False
        profile.is_executive = False
        profile.save()

        body = self.get_serializer(profile).data
        return Response(data=body, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['put'], permission_classes=[IsExecutiveAdmin])
    def maketeacher(self, request, pk=None):
        profile = self.get_object()
        profile.group = None
        profile.classroom = None
        profile.is_student = False
        profile.is_teacher = True
        profile.save()

        body = self.get_serializer(profile).data
        return Response(data=body, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['put'], permission_classes=[IsAdmin])
    def makeexecutive(self, request, pk=None):
        profile = self.get_object()
        profile.group = None
        profile.classroom = None
        profile.is_student = False
        profile.is_executive = True
        profile.save()

        body = self.get_serializer(profile).data
        return Response(data=body, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['put'], permission_classes=[IsTeacherExecutiveAdmin])
    def changeclassroom(self, request, pk=None):
        profile = self.get_object()
        seriazlier = AdminChangeClassRoomSerializer(data=request.data)
        seriazlier.is_valid(raise_exception=True)
        classroom = seriazlier.validated_data['classroom']  # class none yapılabilir.

        if not classroom:
            profile.classroom = None
        else:
            if classroom.area not in Area.objects.filter(Q(executives=request.user) |
                                                         Q(region__admins=request.user)):
                body = {"classroom": "You have not authority on this classroom"}
                return Response(data=body, status=status.HTTP_400_BAD_REQUEST)
            profile.classroom = classroom

        profile.save()

        body = self.get_serializer(profile).data
        return Response(data=body, status=status.HTTP_202_ACCEPTED)


class AdminClassroomViewSet(viewsets.ModelViewSet):
    serializer_class = AdminClassroomSerializer
    permission_classes = (CanEditClassroom,)

    def get_queryset(self):
        if self.request.user.profile.is_executive:
            areas = Area.objects.filter(executives=self.request.user)
            return ClassRoom.objects.filter(area__in=areas)
        else:
            region = Region.objects.filter(admins=self.request.user)
            return ClassRoom.objects.filter(area__region__in=region)

    @action(detail=False, permission_classes=[IsTeacherExecutiveAdmin])
    def myclassrooms(self, request):
        classrooms = ClassRoom.objects.filter(teachers=request.user)

        body = MyClassRoomSerializer(classrooms, many=True).data
        return Response(body, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def teachers(self, request, pk=None):
        classroom = self.get_object()
        teachers = classroom.teachers.all()
        teacher_profiles = Profile.objects.filter(user__in=teachers)

        body = ProfileModelSerializer(teacher_profiles, many=True).data
        return Response(data=body, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], permission_classes=[CanEditClassroom])
    def addteacher(self, request, pk=None):
        classroom = self.get_object()
        serializer = AdminClassroomTeacherSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        classroom.teachers.add(user)
        classroom.save()

        body = self.get_serializer(classroom).data
        return Response(data=body, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['put'], permission_classes=[CanEditClassroom])
    def removeteacher(self, request, pk=None):
        classroom = self.get_object()
        serializer = AdminClassroomTeacherSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user in classroom.teachers.all():
            classroom.teachers.remove(user)
            classroom.save()

        body = self.get_serializer(classroom).data
        return Response(data=body, status=status.HTTP_202_ACCEPTED)


class AdminAreaViewset(viewsets.ModelViewSet):
    serializer_class = AdminAreaSeriazlier
    permission_classes = (IsExecutiveAdmin,)

    def get_queryset(self):
        if self.request.user.profile.is_executive:
            return Area.objects.filter(executives=self.request.user)
        else:
            region = Region.objects.filter(admins=self.request.user)
            return Area.objects.filter(region__in=region)

    @action(detail=False, permission_classes=[IsExecutiveAdmin])
    def myareas(self, request):
        areas = Area.objects.filter(executives=request.user)

        body = MyAreaSerializer(areas, many=True).data
        return Response(body, status=status.HTTP_200_OK)

    @action(detail=False, permission_classes=[IsAdmin])
    def allexecutives(self, request):
        regions = Region.objects.filter(admins=request.user)
        areas = Area.objects.filter(region__in=regions)
        executives = Area.objects.none()
        for a in areas:
            executives = executives | a.executives.all()
        executive_profiles = Profile.objects.filter(user__in=executives)

        body = ProfileModelSerializer(executive_profiles, many=True).data
        return Response(data=body, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def executives(self, request, pk=None):
        area = self.get_object()
        executives = area.executives.all()
        executive_profiles = Profile.objects.filter(user__in=executives)

        body = ProfileModelSerializer(executive_profiles, many=True).data
        return Response(data=body, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def teachers(self, request, pk=None):
        area = self.get_object()
        classrooms = ClassRoom.objects.filter(area=area)
        teachers = User.objects.none()
        for c in classrooms:
            teachers = teachers | c.teachers.all()
        teacher_profiles = Profile.objects.filter(user__in=teachers)

        body = ProfileModelSerializer(teacher_profiles)
        return Response(data=body, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'])
    def addexecutive(self, request, pk=None):
        area = self.get_object()
        serializer = AdminAreaExcutiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        area.executives.add(user)
        area.save()

        body = self.get_serializer(area).data
        return Response(data=body, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['put'])
    def removeexecutive(self, request, pk=None):
        area = self.get_object()
        serializer = AdminAreaExcutiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user in area.executives.all():
            area.executives.remove(user)
            area.save()

        body = self.get_serializer(area).data
        return Response(data=body, status=status.HTTP_202_ACCEPTED)
