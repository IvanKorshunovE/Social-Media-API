from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import redirect
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, status, mixins
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from user.serializers import (
    CreateUserSerializer,
    ReadOnlyUserFollowersSerializer,
    LogoutSerializer,
    ProfileImageSerializer,
)


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
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
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Implement search using username
        and other criteria
        """
        queryset = self.queryset

        username = self.request.query_params.get(
            "username"
        )
        place_of_birth = self.request.query_params.get(
            "place_of_birth"
        )
        start_date = self.request.query_params.get(
            "start_date")
        end_date = self.request.query_params.get(
            "end_date")

        if username:
            queryset = queryset.filter(
                username__icontains=username
            )

        if place_of_birth:
            queryset = queryset.filter(
                place_of_birth__icontains=place_of_birth
            )

        if start_date and end_date:
            queryset = queryset.filter(
                birth_date__range=[
                    start_date,
                    end_date
                ]
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

        if self.request.method == "POST":
            if me == user_you_want_subscribe:
                return Response(
                    {"detail": "You cannot subscribe to yourself."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            has_subscribed = me.following.filter(id=user_you_want_subscribe.id).exists()
            if has_subscribed:
                me.following.remove(user_you_want_subscribe)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                me.following.add(user_you_want_subscribe)
                return Response(status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance == self.request.user:
            return redirect(reverse("user:manage"))
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="start_date",
                description=(
                        "Search by date of birth range"
                        "in format yyyy-mm-dd, "
                        "example url: "
                        "/api/users/users/?start_date=2022-06-11&end_date=2022-06-12"
                ),
                required=False,
                type=str
            ),
            OpenApiParameter(
                name="end_date",
                description=(
                        "Search by date of birth range"
                        "in format yyyy-mm-dd, "
                        "example url: "
                        "/api/users/users/?start_date=2022-06-11&end_date=2022-06-12"
                ),
                required=False,
                type=str
            ),
            OpenApiParameter(
                name="username",
                description="Search by username",
                required=False,
                type=str
            ),
            OpenApiParameter(
                name="place_of_birth",
                description=(
                        "Search by place of birth, "
                        "for example by city, country, etc."
                ),
                required=False,
                type=str
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of users with the
        ability to filter them by username,
        date of birth and place of birth.
        """
        return super().list(request, *args, **kwargs)


class CreateUserView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UploadProfilePictureView(APIView):
    serializer_class = ProfileImageSerializer
    permission_classes = [IsAuthenticated]

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

    def get(self, request, *args, **kwargs):
        """
        Method to retrieve profile image
        """
        profile = self.get_object()
        serializer = ProfileImageSerializer(
            profile
        )
        return Response(
            serializer.data, status.HTTP_200_OK
        )


class LogoutAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    def post(self, request):
        """
        Send a refresh token to this endpoint in order to
        make it invalid
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status.HTTP_204_NO_CONTENT)
