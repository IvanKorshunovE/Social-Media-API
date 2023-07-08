from django.contrib.auth import get_user_model
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user.serializers import (
    UserListSerializer,
    UserSerializer,
    CreateUserSerializer,
    ReadOnlyUserFollowersSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = CreateUserSerializer

    def get_serializer_class(self):
        if self.action == "subscribe":
            return ReadOnlyUserFollowersSerializer

        return CreateUserSerializer

    @action(
        methods=["GET", "PATCH"],
        detail=True,
        url_path="subscribe",
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, pk=None):
        user_you_want_subscribe = self.get_object()
        me = self.request.user
        if self.request.method == "GET":
            subscribers = user_you_want_subscribe.followers.all()
            serializer = self.get_serializer(subscribers, many=True)
            return Response(serializer.data)
        if self.request.method == "PATCH":
            has_subscribed = user_you_want_subscribe.followers.filter(
                id=me.id
            ).exists()
            if has_subscribed:
                user_you_want_subscribe.followers.remove(me)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                user_you_want_subscribe.followers.add(me)
                return Response(status=status.HTTP_201_CREATED)


class CreateUserView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = CreateUserSerializer

    def get_object(self):
        return self.request.user
