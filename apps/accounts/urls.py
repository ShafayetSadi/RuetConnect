from django.urls import include, path

from .views import profile, profile_update

urlpatterns = [
    path("profile/", profile, name="profile"),
    path("profile/update/", profile_update, name="profile-update"),
    # Allauth URLs come after custom views
    path("", include("allauth.urls")),
]
