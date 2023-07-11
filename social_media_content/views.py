from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from social_media_content.models import Post
from social_media_content.serializers import (
    PostSerializer,
    CommentSerializer
)


class PostPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class PostViewSet(viewsets.ModelViewSet):
    queryset = (
        Post.objects.all().prefetch_related(
            "likes", "comments"
        ).select_related("user")
    )
    serializer_class = PostSerializer
    pagination_class = PostPagination

    def get_permissions(self):
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy"
        ]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    @staticmethod
    def _params_to_strings(qs):
        """Converts a string to a list of tag names"""
        return [str(name) for name in qs.split(",")]

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_authenticated:
            ids_of_who_i_follow = list(
                self.request.user.following.values_list(
                    "id",
                    flat=True
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
        """Endpoint to like posts"""
        post = self.get_object()
        user = request.user

        has_liked = post.likes.filter(
            id=user.id
        ).exists()

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
        methods=["POST", "GET"],
        detail=True,
        url_path="comments",
        permission_classes=[IsAuthenticated],
    )
    def comments(self, request, pk=None):
        if self.request.method == "GET":
            post = self.get_object()
            comments = post.comments.all()
            serializer = CommentSerializer(
                comments, many=True
            )

            return Response(serializer.data)

        if self.request.method == "POST":
            post = self.get_object()
            serializer = CommentSerializer(
                data=request.data
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(post=post, user=request.user)

            return Response(status=status.HTTP_201_CREATED)

    @action(
        methods=["GET"],
        detail=False,
        url_path="liked_posts",
        permission_classes=[IsAuthenticated],
    )
    def liked_posts(self, request):
        queryset = self.get_queryset().filter(
            likes=self.request.user
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this post.")
        instance.delete()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
