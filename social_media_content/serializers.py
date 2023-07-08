from django.contrib.auth import get_user_model
from rest_framework import serializers

from social_media_content.models import (
    Post,
    Comment,
)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("text", )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id",)


class PostSerializer(serializers.ModelSerializer):
    likes = UserSerializer(
        many=True, read_only=True
    )
    comments = CommentSerializer(read_only=True, many=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ("id", "title", "text", "user", "likes", "comments")


class PostDetailAddCommentSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(read_only=False, many=True)

    class Meta:
        model = Post
        fields = ("comments",)
        # fields = ("id", "title", "text", "user", "likes", "comments")
