from social_media_content.create_random_post import create_random_post
from social_media_content.models import Post
from celery import shared_task


@shared_task
def count_posts():
    return Post.objects.count()


@shared_task
def create_new_post() -> None:
    return create_random_post()
