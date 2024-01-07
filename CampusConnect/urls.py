
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('campus.urls')),
    path('user/', include('users.urls')),
    # path('r/', include('threads.urls')),
    path('admin/', admin.site.urls),

    path("__reload__/", include("django_browser_reload.urls", namespace="django_browser_reload")),
]
