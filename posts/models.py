from django.conf import settings
from django.db import models


class Tag(models.Model):
    name = models.CharField(
        max_length=50, unique=True
    )

    class Meta:
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(
        null=False, max_length=100
    )
    text = models.TextField()
    created = models.DateTimeField(
        auto_now_add=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="posts",
    )
    tags = models.ManyToManyField(
        Tag, related_name="posts"
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created"]


class Comment(models.Model):
    text = models.TextField()
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="comments",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.text
