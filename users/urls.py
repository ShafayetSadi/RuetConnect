from django.urls import path
from .views import register, login, logout, profile, profile_update

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path("profile/", profile, name="profile"),
    path("profile/update/", profile_update, name="profile-update"),
]
