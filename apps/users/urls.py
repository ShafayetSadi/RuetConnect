from django.urls import path

from .views import login, logout, profile, profile_update, register

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path("profile/", profile, name="profile"),
    path("profile/update/", profile_update, name="profile-update"),
]
