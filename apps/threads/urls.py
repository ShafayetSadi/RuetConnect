from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.ThreadCreateView.as_view(), name="thread-create"),
    path("<slug:thread_name>/", views.ThreadDetailView.as_view(), name="thread-detail"),
    path("<slug:thread_name>/update/", views.ThreadUpdateView.as_view(), name="thread-update"),
    path("<slug:thread_name>/delete/", views.ThreadDeleteView.as_view(), name="thread-delete"),
]
