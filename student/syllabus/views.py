from django.utils.timezone import now
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from student.syllabus.models import Syllabus, Content, UserSyllabus
from .permissions import CanEditSyllabus
from .serializers import SyllabusModelSerializer,\
    AdminUserSyllabusModelSerializer, LevelListSerializer, CourseListSeriazlier, ContentModelSerializer


class ContentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContentModelSerializer
    queryset = Content.objects.all()


class SyllabusViewSet(viewsets.GenericViewSet):
    serializer_class = SyllabusModelSerializer
    filter_fields = ('level', 'course')
    queryset = Syllabus.objects.all()

    @action(detail=False)
    def levels(self, request):
        qs = Syllabus.objects.distinct('level')

        body = LevelListSerializer(qs, many=True).data
        return Response(data=body, status=status.HTTP_200_OK)

    @action(detail=False, url_path='level/(?P<level>[0-9]+)/courses', permission_classes=[AllowAny])
    def levelcourses(self, request, level=None):
        qs = Syllabus.objects.filter(level=level)

        body = CourseListSeriazlier(qs, many=True).data
        return Response(data=body, status=status.HTTP_200_OK)

    @action(detail=True)
    def contents(self, request, pk=None):
        qs = Content.objects.filter(syllabus=pk)

        body = ContentModelSerializer(qs, many=True).data
        return Response(data=body, status=status.HTTP_200_OK)


class AdminUserSyllabusViewSet(viewsets.ModelViewSet):
    serializer_class = AdminUserSyllabusModelSerializer
    filter_fields = ('user', 'user__classroom', 'content__syllabus', 'is_validated')
    permission_classes = (IsAuthenticated, CanEditSyllabus)
    queryset = UserSyllabus.objects.all()

    @action(detail=True, methods=['put'], permission_classes=[IsAuthenticated, CanEditSyllabus])
    def validate(self, request, pk=None):
        us = self.get_object()
        us.is_validated = True
        us.validate_time = now()
        us.validator_user = self.request.user
        us.save()

        body = self.get_serializer(us).data
        return Response(body, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], permission_classes=[IsAuthenticated, CanEditSyllabus])
    def invalidate(self, request, pk=None):
        us = self.get_object()
        us.is_validated = False
        us.validate_time = now()
        us.validator_user = self.request.user
        us.save()

        body = self.get_serializer(us).data
        return Response(body, status=status.HTTP_200_OK)
