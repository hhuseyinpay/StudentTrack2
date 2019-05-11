from django.db.models import Q
from rest_framework import viewsets, mixins, status
from rest_framework.authtoken import views
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from student.account.models import User
from .permissions import IsStaff, CanEditUser, IsOwner
from .serializers import (UserModelSerializer, AdminUserModelSerializer, UserListSerializer)


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


class AdminUserViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = AdminUserModelSerializer
    permission_classes = (IsAuthenticated, IsStaff, CanEditUser)
    queryset = User.objects.all()
    filter_fields = ('classroom',)

    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        else:
            return AdminUserModelSerializer

    @action(detail=False, url_path='classroom/(?P<classroom_id>[0-9]+)', permission_classes=[IsAuthenticated, IsStaff])
    def classroom(self, request, classroom_id=None):
        qs = User.objects.filter(Q(classroom=classroom_id) | Q(classroom_teacher=classroom_id))

        body = UserListSerializer(qs, many=True).data
        return Response(data=body, status=status.HTTP_200_OK)


#########

class Kayit(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        return Response()
