from django.contrib.auth import get_user_model
from rest_framework import serializers

from social_media_content.models import Post


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id",)


class PostSerializer(serializers.ModelSerializer):
    likes = UserSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = Post
        fields = ("id", "title", "text", "user", "likes")
