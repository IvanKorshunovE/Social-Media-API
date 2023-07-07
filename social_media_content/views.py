from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_media_content.models import Post
from social_media_content.serializers import PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @action(
        methods=["PATCH"],
        detail=True,
        url_path="like-this-post",
        permission_classes=[IsAuthenticated],
    )
    def like_this_post(self, request, pk=None):
        """Endpoint to like posts"""
        post = self.get_object()
        user = request.user

        has_liked = post.likes.filter(id=user.id).exists()

        if has_liked:
            post.likes.remove(user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            post.likes.add(user)
            return Response(status=status.HTTP_201_CREATED)
