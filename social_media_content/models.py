from django.conf import settings
from django.db import models


class Post(models.Model):
    title = models.CharField(null=False, max_length=100)
    text = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_posts'
    )
    # likes = models.IntegerField(default=0)
