from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("apps.campus.urls")),
    path("r/", include("apps.threads.urls")),
    path("post/", include("apps.posts.urls")),
    path("comment/", include("apps.comments.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path(
            "__reload__/",
            include("django_browser_reload.urls", namespace="django_browser_reload"),
        )
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
