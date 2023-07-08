from django.contrib.auth import get_user_model
from rest_framework import viewsets, generics

from user.serializers import (
    UserListSerializer,
    UserSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserListSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

