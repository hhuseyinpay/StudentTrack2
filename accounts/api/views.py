from django.db.models import Q
from rest_framework import generics, viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken import views
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import Profile, ClassRoom, Groups, Area, Region
from .permissions import IsTeExAd
from .serializer import ProfileModelSerializer, PClassSerializer, PGroupSerializer, \
    AdminProfileModelSerializer, AdminProfileCreateSerializer, AdminProfileUpdateSerializer


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
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        return Profile.objects.all()


class ProfileViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = ProfileModelSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        return Profile.objects.filter(id=self.request.user.profile.id)


class AdminMyClassroomList(generics.ListAPIView):
    serializer_class = PClassSerializer
    permission_classes = (IsAuthenticated, IsTeExAd)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        user = self.request.user
        # bu sorgu sadeleştirilmeli....
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
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_fields = ('classroom', 'related_area', 'related_region', 'is_student', 'is_teacher')

    def create(self, request, *args, **kwargs):
        serializer = AdminProfileCreateSerializer(data=request.data, context={'current_user': self.request.user})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        current_user = request.user
        current_profile = current_user.profile  # currunt profile
        error_respons = {}

        if current_profile.is_teacher and not current_profile.is_executive:
            if not data.get('is_student', False):
                error_respons['is_student'] = "You can only create a student."

            if data.get('is_teacher', False) or data.get('is_executive', False) or data.get('is_admin', False):
                error_respons['authority'] = "You cannot create a higher authority."

            if data['classroom'] not in ClassRoom.objects.filter(teachers=current_user):
                print(data['classroom'])
                print(ClassRoom.objects.filter(teachers=current_user))
                error_respons['classroom'] = "You cannot assign classroom that you are not teacher"

        elif current_profile.is_executive:
            if data.get('is_student', False) and data.get('is_teacher', False):
                error_respons['is_student-is_teacher'] = "The profile cannot be student and teacher in the same time."

            if data.get('is_executive', False) or data.get('is_admin', False):
                error_respons['authority'] = "You cannot create a higher authority."

            if data.get('is_student', False) and \
                    data['classroom'] not in ClassRoom.objects.filter(Q(related_area__executives=current_user) |
                                                                      Q(teachers=current_user)):
                error_respons['classroom'] = "You cannot assign classroom that you are not executive"

        elif current_profile.is_admin:
            if data.get('is_student', False):
                if data.get('is_teacher', False) or data.get('is_executive', False):
                    error_respons['is_*'] = "The profile cannot be student and (teacher or executive) in the same time."

            if data.get('is_admin', False):
                error_respons['authority'] = "You cannot create a higher authority."

            if data['classroom'] not in ClassRoom.objects.filter(related_area__related_region__admins=current_user):
                error_respons['classroom'] = "You cannot assign classroom that you are not executive"

        if error_respons:
            return Response({'error': error_respons}, status=status.HTTP_403_FORBIDDEN)

        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        user_profile = self.get_object()
        user_user = user_profile.user
        serializer = AdminProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        current_user = request.user
        current_profile = current_user.profile  # currunt profile
        error_respons = {}

        if current_profile.is_teacher and not current_profile.is_executive:
            if user_profile.classroom not in ClassRoom.objects.filter(teachers=current_user):
                return Response({'error': "You cannot edit this profile"}, status=status.HTTP_403_FORBIDDEN)

            if not data.get('is_student', True):  # bu fieldı göndermediyse sıkıntı yok
                error_respons['is_student'] = "You cannot change the student."

            if data.get('is_teacher', False) or data.get('is_executive', False) or data.get('is_admin', False):
                error_respons['authority'] = "You cannot create a higher authority."

            if data.get('classroom', False) and \
                    data['classroom'] not in ClassRoom.objects.filter(teachers=current_user):
                error_respons['classroom'] = "You cannot assign classroom that you are not teacher"

        elif current_profile.is_executive:
            # currunt_profile hem teacher hem executive olabilir. Onun için hem classroom hem area'ya bakılıyor.
            if user_profile.classroom not in \
                    ClassRoom.objects.filter(related_area__executives=current_user) or \
                    user_profile.related_area not in \
                    Area.objects.filter(executives=current_user):
                return Response({'error': "You cannot edit this profile"}, status=status.HTTP_403_FORBIDDEN)

            if data.get('is_student', False) and data.get('is_teacher', False):
                error_respons['is_student-is_teacher'] = "The profile cannot be student and teacher in the same time."

            if data.get('is_executive', False) or data.get('is_admin', False):
                error_respons['authority'] = "You cannot create a higher authority."

            if data.get('classroom', False) and \
                    data['classroom'] not in ClassRoom.objects.filter(related_area__executives=current_user):
                error_respons['classroom'] = "You cannot assign classroom that you are not executive"

        elif current_profile.is_admin:
            if user_profile.related_region not in Region.objects.filter(admins=current_user):
                return Response({'error': "You cannot edit this profile"}, status=status.HTTP_403_FORBIDDEN)

            if data.get('is_student', False):
                if data.get('is_teacher', False) or data.get('is_executive', False):
                    error_respons['is_*'] = "The profile cannot be student and (teacher or executive) in the same time."

            if data.get('is_admin', False):
                error_respons['authority'] = "You cannot create a higher authority."

            if data['classroom'] not in ClassRoom.objects.filter(related_area__related_region__admins=current_user):
                error_respons['classroom'] = "You cannot assign classroom that you are not executive"

        if error_respons:
            return Response({'error': error_respons}, status=status.HTTP_403_FORBIDDEN)

        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)
