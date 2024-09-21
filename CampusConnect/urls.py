from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('', include('campus.urls')),

    path('user/', include('users.urls')),
    # user redirects
    path('login/', RedirectView.as_view(url='/user/login/')),
    path('logout/', RedirectView.as_view(url='/user/logout/')),
    path('register/', RedirectView.as_view(url='/user/register/')),

    path('r/', include('threads.urls')),

    path('post/', include('posts.urls')),

    path('comment/', include('comments.urls')),

    path('admin/', admin.site.urls),

    path("__reload__/", include("django_browser_reload.urls", namespace="django_browser_reload")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
