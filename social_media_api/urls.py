from django.conf import settings
from django.conf.urls.static import static
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
    path("__debug__/", include("debug_toolbar.urls")),
] + static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
