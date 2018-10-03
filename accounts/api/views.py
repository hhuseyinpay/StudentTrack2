from django.db.models import Q
from rest_framework import generics, viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken import views
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Profile, ClassRoom, Groups
from .permissions import IsTeExAd, CanEditProfile
from .serializer import ProfileModelSerializer, ProfileRetrieveUpdateDestroySeriazlizer, ListProfileSerializer, \
    ProfileCreateSerializer, PClassSerializer, PGroupSerializer, AdminProfileModelSerializer, \
    AdminProfileCreateSerializer


class UserLoginAPIView(views.ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'user': user.id, 'token': token.key})


class ProfileListAPIView(generics.ListAPIView):
    serializer_class = ProfileRetrieveUpdateDestroySeriazlizer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        return Profile.objects.user(self.request.user)


class ListAllProfileAPIView(generics.ListAPIView):
    serializer_class = ListProfileSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        return Profile.objects.all()


class ClassRoomProfileListAPIView(generics.ListAPIView):
    serializer_class = ProfileRetrieveUpdateDestroySeriazlizer
    permission_classes = (IsAuthenticated, IsTeExAd)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        teacher = self.request.user
        classroom = self.kwargs.get('classroom')
        return Profile.objects.filter(classroom=classroom, classroom__teachers=teacher,
                                      is_teacher=False, is_executive=False, is_admin=False)


class AreaProfileListAPIView(generics.ListAPIView):
    serializer_class = ListProfileSerializer
    permission_classes = (IsAuthenticated, IsTeExAd)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        area = self.kwargs.get('area')
        return Profile.objects.filter(related_area=area)


class RegionProfileListAPIView(generics.ListAPIView):
    serializer_class = ListProfileSerializer
    permission_classes = (IsAuthenticated, IsTeExAd)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        region = self.kwargs.get('region')
        return Profile.objects.filter(related_region=region)


class ProfileViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = ProfileModelSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        return Profile.objects.user(self.request.user)

    def get_object(self):
        return Profile.objects.user(self.request.user)


class OLD_ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileRetrieveUpdateDestroySeriazlizer
    permission_classes = (IsAuthenticated, IsTeExAd)
    authentication_classes = (TokenAuthentication,)
    lookup_field = 'id'

    # authentication_classes = [JSONWebTokenAuthentication, ]

    # def get_object(self):
    #    return Profile.objects.all()

    #     user = self.request.user
    #     profile = user.profile
    #     url_paramter = self.kwargs.get('id')
    #     try:
    #         obj = Profile.objects.get(id=url_paramter)
    #     except ObjectDoesNotExist:
    #         return None
    #     if user in obj.classroom.teachers.all() or \
    #             user in obj.related_area.executives.all() or \
    #             user in obj.related_region.admin.all():
    #         return obj
    #     return None

    def get_queryset(self):
        user = self.request.user
        profile = user.profile

        qs = Profile.objects.none()
        t = Profile.objects.none()
        a = Profile.objects.none()
        r = Profile.objects.none()

        if profile.is_teacher:
            t = Profile.objects.filter(classroom=profile.classroom,
                                       is_teacher=False, is_executive=False, is_admin=False)
        if profile.is_executive:
            a = Profile.objects.filter(related_area=profile.related_area, is_executive=False, is_admin=False)
        if profile.is_admin:
            r = Profile.objects.filter(related_region=profile.related_region, is_admin=False)

        return qs.union(t, a, r).distinct()

    def get_serializer_context(self):
        return {'user': self.request.user}


#
#
# class ProfileCreateAPIView(generics.ListCreateAPIView):
#     serializer_class = ProfileCreateSeriazlizer
#     permission_classes = (IsAuthenticated, CanEditProfile,)
#     queryset = Profile.objects.all()
#
#     def get_serializer_context(self):
#         """
#         Extra context provided to the serializer class.
#         """
#         return {
#             'user': self.request.user,
#         }
#
#
# # class Profile
#


class ProfileCreateAPIView(generics.CreateAPIView):
    serializer_class = ProfileCreateSerializer
    permission_classes = (IsAuthenticated, IsTeExAd)
    authentication_classes = (TokenAuthentication,)

    def get_serializer_context(self):
        return {'user': self.request.user}


class ProfileRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileRetrieveUpdateDestroySeriazlizer
    permission_classes = (IsAuthenticated, CanEditProfile)
    lookup_field = 'id'

    def get_queryset(self):
        return Profile.objects.filter(id=self.kwargs['id'])

    def get_serializer_context(self):
        return {'user': self.request.user}
    # def get_queryset(self):
    #     user = self.request.user
    #     profile = user.profile
    #     if profile.is_teacher:
    #         return Profile.objects.filter(
    #             Q(user=user) | Q(classroom__teachers=user)
    #         ).distinct()
    #     if profile.is_executive:
    #         return Profile.objects.filter(
    #             Q(user=user) |
    #             Q(classroom__teachers=user) |
    #             Q(classroom__related_area__executives=user) |
    #             Q(classroom__related_area__related_region__executives=user)
    #         ).distinct()
    #     return None


class AdminMyClassroomList(generics.ListAPIView):
    serializer_class = PClassSerializer
    permission_classes = (IsAuthenticated, IsTeExAd)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        user = self.request.user

        return ClassRoom.objects.filter(Q(teachers=user) |
                                        Q(related_area__executives=user) |
                                        Q(related_area__related_region__admins=user)).distinct()


class AdminGroupList(generics.ListAPIView):
    serializer_class = PGroupSerializer
    # permission_classes = (IsAuthenticated, IsTeExAd)
    # authentication_classes = (TokenAuthentication,)
    queryset = Groups.objects.all()


class AdminProfileViewSet(viewsets.ModelViewSet):
    serializer_class = AdminProfileModelSerializer
    permission_classes = (IsAuthenticated, IsTeExAd)
    authentication_classes = (TokenAuthentication,)

    queryset = Profile.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = AdminProfileCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        current_user = request.user
        current_profile = current_user.profile  # currunt profile
        error_respons = {}

        if current_profile.is_teacher:  # and not current_profile.is_executive:
            if not data.get('is_student', False):
                error_respons['is_student'] = "You can only create a student."

            if data.get('is_teacher', False) or data.get('is_executive', False) or data.get('is_admin', False):
                error_respons['authority'] = "You cannot create a higher authority."
            # print(ClassRoom.objects.filter(teachers=current_user, id=data['classroom'].id))
            if data['classroom'] not in ClassRoom.objects.filter(teachers=current_user):
                error_respons['classroom'] = "You cannot assign classroom that you are not teacher"

        elif current_profile.is_executive:
            if data.get('is_student', False) and data.get('is_teacher', False):
                error_respons['is_student-is_teacher'] = "The profile cannot be student and teacher in the same time."

            if data.get('is_executive', False) or data.get('is_admin', False):
                error_respons['authority'] = "You cannot create a higher authority."

            if data['classroom'] not in ClassRoom.objects.filter(related_area__executives=current_user):
                error_respons['classroom'] = "You cannot assign classroom that you are not executive"

        elif current_profile.is_executive:
            if data.get('is_student', False):
                if data.get('is_teacher', False) or data.get('is_executive', False):
                    error_respons['is_*'] = "The profile cannot be student and (teacher or executive) in the same time."

            if data.get('is_admin', False):
                error_respons['authority'] = "You cannot create a higher authority."

            if data['classroom'] not in ClassRoom.objects.filter(related_area__related_region__admins=current_user):
                error_respons['classroom'] = "You cannot assign classroom that you are not executive"

        if error_respons:
            return Response({'error': error_respons}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'status': "ups"})
