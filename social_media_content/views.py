from urllib.parse import urlencode

from django.shortcuts import redirect
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter
)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.reverse import reverse

from social_media_content.models import Post, Comment
from social_media_content.pagination import PostPagination
from social_media_content.permissions import IsOwnerOrReadOnly
from social_media_content.serializers import (
    PostSerializer,
    CommentSerializer
)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = self.queryset
        post_id = self.request.query_params.get("post_id")
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(
            post_id=self.request.query_params.get("post_id"),
            user_id=self.request.user.id,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="Post ID",
                description=(
                        "Filter by post id "
                        "(post ID automatically "
                        "returns as query parameter "
                        "from comments custom action "
                        "in PostViewSet)"
                ),
                required=False,
                type=str
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of comments with the ability
        to filter them by post id (mostly required
        for comments custom action in PostViewSet.
        """
        return super().list(request, *args, **kwargs)


class PostViewSet(viewsets.ModelViewSet):
    queryset = (
        Post.objects.all()
        .prefetch_related(
            "likes", "comments"
        ).select_related("user")
    )
    serializer_class = PostSerializer
    pagination_class = PostPagination

    def get_permissions(self):
        if self.action in [
            "update", "partial_update", "destroy"
        ]:
            permission_classes = [IsOwnerOrReadOnly]
        elif self.action in [
            "like_this_post", "liked_posts"
        ]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [
            permission() for permission
            in permission_classes
        ]

    @staticmethod
    def _params_to_strings(qs):
        """Converts a string to a list of tag names"""
        return [str(name) for name in qs.split(",")]

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_authenticated:
            ids_of_who_i_follow = list(
                self.request.user.following.values_list(
                    "id", flat=True
                )
            )
            my_id = self.request.user.id
            ids_of_who_i_follow.append(my_id)
            queryset = queryset.filter(
                user_id__in=ids_of_who_i_follow
            ).distinct()
        tags = self.request.query_params.get("tags")
        if tags:
            tags = self._params_to_strings(tags)
            queryset = queryset.filter(
                tags__name__in=tags
            )
        return queryset.distinct()

    @action(
        methods=["PATCH"],
        detail=True,
        url_path="like",
        permission_classes=[IsAuthenticated],
    )
    def like_this_post(self, request, pk=None):
        """
        Endpoint to like posts,
        like is user instance (particularly user ID)
        """
        post = self.get_object()
        user = request.user

        has_liked = post.likes.filter(id=user.id).exists()

        if has_liked:
            post.likes.remove(user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            post.likes.add(user)
            return Response(status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.action == "comments":
            return CommentSerializer

        return PostSerializer

    @action(
        methods=["GET"],
        detail=True,
        url_path="comments",
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def comments(self, request, pk=None):
        """
        Returns all comments related to particular post,
        this endpoint redirects to 'social_media_content:comment-list'
        endpoint. The url example is:
        When you type /api/content/posts/1/comments/
        in url bar, you will be redirected to:
        /api/content/comments/?post_id=1
        """
        if self.request.method == "GET":
            post = self.get_object()
            post_id = post.id
            query_params = urlencode({"post_id": post_id})
            redirect_url = (
                    reverse(
                        "social_media_content:comment-list"
                    ) + "?" + query_params
            )
            return redirect(redirect_url)

    @action(
        methods=["GET"],
        detail=False,
        url_path="liked_posts",
        permission_classes=[IsAuthenticated],
    )
    def liked_posts(self, request):
        """
        Returns all posts that you liked
        """
        queryset = self.get_queryset().filter(
            likes=self.request.user
        )
        serializer = self.get_serializer(
            queryset, many=True
        )
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied(
                "You do not have permission to delete this post."
            )
        instance.delete()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="tags",
                description="Filter by tags",
                required=False,
                type=str
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of posts with the
        ability to filter them by tags.
        """
        return super().list(request, *args, **kwargs)
