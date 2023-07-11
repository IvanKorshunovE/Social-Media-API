from django.contrib import admin

from social_media_content.models import Post, Comment, Tags

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Tags)
