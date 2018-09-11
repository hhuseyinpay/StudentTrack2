from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, QuerySet
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from .serializer import ProfileModelSerializer, ProfileRetrieveUpdateDestroySeriazlizer, ListProfileSerializer, \
    ProfileCreateSerializer
from .permissions import IsTeExAd, CanEditProfile
from accounts.models import Profile


class ProfileListAPIView(generics.ListAPIView):
    serializer_class = ProfileModelSerializer
    permission_classes = (IsAuthenticated,)

    # authentication_classes = [JSONWebTokenAuthentication, ]

    def get_queryset(self):
        return Profile.objects.user(self.request.user)


class ListAllProfileAPIView(generics.ListAPIView):
    serializer_class = ListProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Profile.objects.all()


class ClassRoomProfileListAPIView(generics.ListAPIView):
    serializer_class = ListProfileSerializer
    permission_classes = (IsAuthenticated,)

    # authentication_classes = [JSONWebTokenAuthentication, ]

    def get_queryset(self):
        classroom = self.kwargs.get('classroom')
        return Profile.objects.filter(classroom=classroom)


class AreaProfileListAPIView(generics.ListAPIView):
    serializer_class = ListProfileSerializer
    permission_classes = (IsAuthenticated,)

    # authentication_classes = [JSONWebTokenAuthentication, ]

    def get_queryset(self):
        area = self.kwargs.get('area')
        return Profile.objects.filter(related_area=area)


class RegionProfileListAPIView(generics.ListAPIView):
    serializer_class = ListProfileSerializer
    permission_classes = (IsAuthenticated,)

    # authentication_classes = [JSONWebTokenAuthentication, ]

    def get_queryset(self):
        region = self.kwargs.get('region')
        return Profile.objects.filter(related_region=region)


class ProfileViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsTeExAd,)
    serializer_class = ProfileRetrieveUpdateDestroySeriazlizer
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

    # authentication_classes = [JSONWebTokenAuthentication, ]

    def get_serializer_context(self):
        return {'user': self.request.user}


class ProfileRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileRetrieveUpdateDestroySeriazlizer
    permission_classes = (IsAuthenticated, CanEditProfile,)
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
