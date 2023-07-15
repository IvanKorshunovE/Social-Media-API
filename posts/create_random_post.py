from django.contrib.auth import get_user_model
import friendlywords as fw
from posts.models import Post


def create_random_post():
    user = get_user_model().objects.first()
    title = fw.generate(2)
    text = fw.generate(60)
    Post.objects.create(
        title=title,
        text=text,
        user=user
    )
