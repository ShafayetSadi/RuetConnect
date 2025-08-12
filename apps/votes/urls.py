from django.urls import path

from . import views

urlpatterns = [
    path("vote/", views.vote, name="vote"),
    path("save/<slug:slug>/", views.toggle_save_post, name="toggle-save-post"),
]
