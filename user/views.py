from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import generics, status, mixins
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from user.serializers import (
    CreateUserSerializer,
    ReadOnlyUserFollowersSerializer,
    LogoutSerializer, ProfileImageSerializer
)


class UserPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = (
        get_user_model().objects.all()
        .annotate(
            followings=Count("following")
        )
    )
    serializer_class = CreateUserSerializer
    pagination_class = UserPagination

    def get_queryset(self):
        """
        Implement search using username
        and other criteria
        """
        queryset = self.queryset

        username = self.request.query_params.get(
            "username"
        )
        birth_date = self.request.query_params.get(
            "birth_date"
        )
        place_of_birth = self.request.query_params.get(
            "place_of_birth"
        )

        if username:
            queryset = queryset.filter(
                username__icontains=username
            )

        if birth_date:
            queryset = queryset.filter(
                birth_date=birth_date
            )

        if place_of_birth:
            queryset = queryset.filter(
                place_of_birth__icontains=place_of_birth
            )

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "subscribe":
            return ReadOnlyUserFollowersSerializer

        return CreateUserSerializer

    @action(
        methods=["GET"],
        detail=True,
        url_path="profile_picture",
        permission_classes=[IsAuthenticated],
    )
    def retrieve_profile_picture(self, request, pk=None):
        profile = self.get_object()
        serializer = ProfileImageSerializer(profile, many=False)
        return Response(serializer.data)

    @action(
        methods=["GET"],
        detail=False,
        url_path="following",
        permission_classes=[IsAuthenticated],
    )
    def who_i_am_following(self, request):
        """
        The endpoint to see users that I
        (current user) am subscribed to
        """
        who_i_am_following = self.request.user.following.all()
        serializer = self.get_serializer(who_i_am_following, many=True)
        return Response(serializer.data)

    @action(
        methods=["GET"],
        detail=False,
        url_path="my_followers",
        permission_classes=[IsAuthenticated],
    )
    def my_followers(self, request):
        """
        The endpoint to see users that are subscribed to me (current user)
        """
        my_followers = self.request.user.followers.all()
        serializer = self.get_serializer(my_followers, many=True)
        return Response(serializer.data)

    @action(
        methods=["GET", "POST"],
        detail=True,
        url_path="subscribe",
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, pk=None):
        """
        The endpoint to subscribe or, if already subscribed,
        unsubscribe current user from other users
        """
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

            has_subscribed = me.following.filter(
                id=user_you_want_subscribe.id
            ).exists()
            if has_subscribed:
                me.following.remove(user_you_want_subscribe)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                me.following.add(user_you_want_subscribe)
                return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """
        The endpoint to delete current user's account
        """
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


class UploadProfilePictureView(
    APIView
):
    serializer_class = ProfileImageSerializer

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        """
        Method to upload profile image
        """
        profile = self.get_object()
        serializer = ProfileImageSerializer(
            profile, data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )


class LogoutAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status.HTTP_204_NO_CONTENT)
