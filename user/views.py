from django.contrib.auth import get_user_model
from rest_framework import generics, status, mixins
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from user.serializers import (
    CreateUserSerializer,
    ReadOnlyUserFollowersSerializer,
    LogoutSerializer
)


class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = get_user_model().objects.all()
    serializer_class = CreateUserSerializer
    pagination_class = UserPagination

    def get_serializer_class(self):
        if self.action == "subscribe":
            return ReadOnlyUserFollowersSerializer

        return CreateUserSerializer

    @action(
        methods=["GET", "POST"],
        detail=True,
        url_path="subscribe",
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, pk=None):
        user_you_want_subscribe = self.get_object()
        me = self.request.user
        if self.request.method == "GET":
            subscribers = user_you_want_subscribe.followers.all()
            page = self.paginate_queryset(subscribers)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(subscribers, many=True)
            return Response(serializer.data)
        if self.request.method == "POST":
            if me == user_you_want_subscribe:
                return Response(
                    {
                        "detail": "You cannot subscribe to yourself."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            has_subscribed = user_you_want_subscribe.followers.filter(
                id=me.id
            ).exists()
            if has_subscribed:
                user_you_want_subscribe.followers.remove(me)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                user_you_want_subscribe.followers.add(me)
                return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        me = request.user

        if instance == me:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {
                    "detail": "You do not have permission to delete this user."
                },
                status=status.HTTP_403_FORBIDDEN
            )


class CreateUserView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = CreateUserSerializer

    def get_object(self):
        return self.request.user


class LogoutAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status.HTTP_204_NO_CONTENT)
