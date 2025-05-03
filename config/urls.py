from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('', include('apps.campus.urls')),

    path('user/', include('apps.users.urls')),
    # user redirects
    path('login/', RedirectView.as_view(url='/user/login/')),
    path('logout/', RedirectView.as_view(url='/user/logout/')),
    path('register/', RedirectView.as_view(url='/user/register/')),

    path('r/', include('apps.threads.urls')),

    path('post/', include('apps.posts.urls')),

    path('comment/', include('apps.comments.urls')),

    path('admin/', admin.site.urls),

    path("__reload__/", include("django_browser_reload.urls", namespace="django_browser_reload")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
