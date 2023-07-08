from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/content/", include(
        "social_media_content.urls",
        namespace="social_media_content"
    )
         ),
    path("api/users/", include(
        "user.urls",
        namespace="user"
    )
         ),
]
