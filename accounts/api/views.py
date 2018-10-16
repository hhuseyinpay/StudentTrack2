from django.db.models import Q
from rest_framework import generics, viewsets, mixins, status
from rest_framework.authtoken import views
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import Profile, ClassRoom, Groups, Area, Region
from .permissions import IsTeacherExecutiveAdmin, IsExecutiveAdmin, IsAdmin, IsTeacher, CanEditClassroom, CanEditProfile
from .serializer import (
    ProfileModelSerializer, PClassSerializer, PGroupSerializer, \
    AdminProfileModelSerializer, AdminProfileCreateSerializer, AdminMakeStudentSeriazlier, \
    AdminChangeClassRoomSerializer, AdminChangeAreaSerializer, \
    AdminClassroomTeacher, AdminClassroomSerializer, AdminAreaSeriazlier
)


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


class ProfileViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = ProfileModelSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Profile.objects.filter(id=self.request.user.profile.id)


class AdminGroupList(generics.ListAPIView):
    serializer_class = PGroupSerializer
    # permission_classes = (IsAuthenticated, IsTeExAd)
    queryset = Groups.objects.all()


class AdminProfileViewSet(viewsets.ModelViewSet):
    serializer_class = AdminProfileModelSerializer
    permission_classes = (IsAuthenticated, CanEditProfile)
    queryset = Profile.objects.all()
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('is_student', 'is_teacher', 'is_executive', 'classroom', 'related_area', 'related_region')

    def create(self, request, *args, **kwargs):
        serializer = AdminProfileCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(request.user.profile.related_region)
        serializer.save(created_by=request.user,
                        related_region=request.user.profile.related_region)  # her yeni profil student olarak başlar
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = AdminProfileCreateSerializer(instance, data=request.data, partial=True)
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

        if classroom not in ClassRoom.objects.filter(teachers=request.user) and \
                classroom.related_area not in Area.objects.filter(Q(executives=request.user) |
                                                                  Q(related_region__admins=request.user)):
            body = {"classroom": "You have not authority on this classroom"}
            return Response(data=body, status=status.HTTP_400_BAD_REQUEST)

        profile.group = group
        profile.classroom = classroom
        profile.related_area = classroom.related_area
        profile.related_region = classroom.related_area.related_region
        profile.is_student = True
        profile.is_teacher = False
        profile.is_executive = False
        profile.save()

        body = self.get_serializer(profile).data
        return Response(data=body, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['put'], permission_classes=[IsExecutiveAdmin])
    def maketeacher(self, request, pk=None):
        profile = self.get_object()

        profile.is_student = False
        profile.is_teacher = True
        profile.save()

        body = self.get_serializer(profile).data
        return Response(data=body, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['put'], permission_classes=[IsAdmin])
    def makeexecutive(self, request, pk=None):
        profile = self.get_object()

        profile.is_student = False
        profile.is_executive = True
        profile.save()

        body = self.get_serializer(profile).data
        return Response(data=body, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['put'], permission_classes=[IsExecutiveAdmin])
    def changeclassroom(self, request, pk=None):
        profile = self.get_object()
        seriazlier = AdminChangeClassRoomSerializer(request.data)
        seriazlier.is_valid(raise_exception=True)
        classroom = seriazlier.validated_data['classroom']  # class none yapılabilir.

        if not classroom:
            profile.classroom = None
        else:
            if classroom.related_area not in Area.objects.filter(Q(executives=request.user) |
                                                                 Q(related_region__admins=request.user)):
                body = {"classroom": "You have not authority on this classroom"}
                return Response(data=body, status=status.HTTP_400_BAD_REQUEST)
            profile.classroom = classroom
            profile.related_area = classroom.related_area
            profile.related_region = classroom.related_area.related_region

        profile.save()

        body = self.get_serializer(profile).data
        return Response(data=body, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['put'], permission_classes=[IsExecutiveAdmin])
    def changearea(self, request, pk=None):
        profile = self.get_object()
        seriazlier = AdminChangeAreaSerializer(request.data)
        seriazlier.is_valid(raise_exception=True)
        related_area = seriazlier.validated_data['related_area']  # class none yapılabilir.

        if not related_area:
            profile.related_area = None
        else:
            if related_area.related_region not in Region.objects.filter(admins=request.user):
                body = {"area": "You have not authority on this area"}
                return Response(data=body, status=status.HTTP_400_BAD_REQUEST)

            profile.related_area = related_area
            profile.related_region = related_area.related_region

        profile.classroom = None
        profile.save()

        body = self.get_serializer(profile).data
        return Response(data=body, status=status.HTTP_202_ACCEPTED)


class AdminClassroomViewSet(viewsets.ModelViewSet):
    serializer_class = AdminClassroomSerializer
    permission_classes = (CanEditClassroom,)

    def get_queryset(self):
        if self.request.user.profile.is_executive:
            return ClassRoom.objects.filter(related_area=self.request.user.profile.related_area)
        else:
            return ClassRoom.objects.filter(related_area__related_region=self.request.user.profile.related_region)

    @action(detail=False, permission_classes=[IsTeacher])
    def myclassrooms(self, request):
        classrooms = ClassRoom.objects.filter(teachers=request.user)
        serializer = PClassSerializer(classrooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'])
    def addteacher(self, request, pk=None):
        classroom = self.get_object()
        serializer = AdminClassroomTeacher(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        classroom.teachers.add(user)
        classroom.save()

        body = self.get_serializer(classroom).data
        return Response(data=body, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['put'])
    def removeteacher(self, request, pk=None):
        classroom = self.get_object()
        serializer = AdminClassroomTeacher(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user in classroom.teachers.all():
            classroom.teachers.remove(user)
            classroom.save()

        body = self.get_serializer(classroom).data
        return Response(data=body, status=status.HTTP_202_ACCEPTED)


class AdminAreaViewset(viewsets.ModelViewSet):
    serializer_class = AdminAreaSeriazlier
    permission_classes = (IsAdmin,)

    def get_queryset(self):
        return Area.objects.filter(related_region=self.request.user.profile.related_region)
