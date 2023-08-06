from posts.create_random_post import create_random_post
from celery import shared_task


@shared_task
def create_new_post() -> None:
    return create_random_post()
