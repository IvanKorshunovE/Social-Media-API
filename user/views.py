from django.contrib.auth import get_user_model
from rest_framework import viewsets

from user.serializers import UserListSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserListSerializer
