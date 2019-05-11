from django.db.models import Case, When, OuterRef, Subquery, Q, BooleanField
from django.utils.timezone import now
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from student.account.permissions import IsStaff
from student.syllabus.models import Syllabus, Content, UserSyllabus
from .permissions import CanEditSyllabus, IsSyllabusOwner
from .serializers import SyllabusModelSerializer, UserSyllabusModelSerializer, AdminUserSyllabusSerializerV2, \
    AdminUserSyllabusModelSerializer, LevelListSerializer, CourseListSeriazlier, ContentModelSerializer, \
    UserContentSerializer, UserSyllabusSerializerV2, AdminUserSyllabusBulkUpdateSeriazlier


class ContentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContentModelSerializer
    queryset = Content.objects.all()


class SyllabusViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
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


class UserSyllabusViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                          mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = UserSyllabusModelSerializer
    filter_fields = ('content__syllabus__level', 'content__syllabus__course', 'is_validated')
    permission_classes = (IsAuthenticated, IsSyllabusOwner)

    # queryset = UserSyllabus.objects.all()

    def get_queryset(self):
        return UserSyllabus.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_validated:
            body = {'detail': 'Onaylanmış bir kuru silemezsiniz.'}
            return Response(data=body, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, url_path='level/(?P<level>[0-9]+)/course/(?P<course_id>[0-9]+)',
            permission_classes=[IsAuthenticated])
    def contents(self, request, level=None, course_id=None):
        usersyllabus = UserSyllabus.objects.filter(user=request.user, content=OuterRef('id'))
        contents = Content.objects.filter(syllabus__level=level, syllabus__course_id=course_id) \
            .annotate(
            user_syllabus_id=Subquery(usersyllabus.values('id')[:1]),
            is_done=Case(When(Q(user_syllabus_id=None), then=False), default=True, output_field=BooleanField()),
            is_validated=Case(When(~Q(user_syllabus_id=None), then=Subquery(usersyllabus.values('is_validated')[:1])),
                              default=False, output_field=BooleanField())
        )

        body = UserContentSerializer(contents, many=True).data
        return Response(body)


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

    @action(detail=False, url_path='notvalidated/user/(?P<user_id>[0-9]+)',
            permission_classes=[IsAuthenticated, IsStaff])
    def notvalidated(self, request, user_id=None):
        us = UserSyllabus.objects.filter(user=user_id)

        body = self.get_serializer(us, many=True).data
        return Response(body, status=status.HTTP_200_OK)
