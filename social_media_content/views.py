from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_media_content.models import Post, Comment
from social_media_content.serializers import PostSerializer, CommentSerializer, PostDetailAddCommentSerializer


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
        if self.request.method == 'GET':
            post = self.get_object()
            comments = post.comments.all()
            serializer = CommentSerializer(comments, many=True)

            return Response(serializer.data)

        if self.request.method == 'POST':
            post = self.get_object()
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                # user = serializer.data['user']
                text = serializer.data['text']
                Comment.objects.create(
                    post=post,
                    # user=user,
                    text=text
                )

                return Response(status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
