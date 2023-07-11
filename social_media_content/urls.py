from django.urls import path, include
from rest_framework import routers

from social_media_content.views import PostViewSet, CommentViewSet

router = routers.DefaultRouter()
router.register("posts", PostViewSet)
router.register("comments", CommentViewSet)


urlpatterns = [
    path("", include(router.urls)),
]

app_name = "social_media_content"
