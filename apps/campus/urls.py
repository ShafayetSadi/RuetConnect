from django.urls import path

from .views import about, home, search

urlpatterns = [
    path("", home, name="campus-home"),
    path("about/", about, name="campus-about"),
    path("search/", search, name="campus-search"),
]
