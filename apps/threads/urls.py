from django.urls import path

from . import views

urlpatterns = [
    path("create/", views.ThreadOrgSelectView.as_view(), name="thread-select-org"),
    path("create/<slug:org_slug>/", views.ThreadCreateView.as_view(), name="thread-create"),
    path("<slug:thread_name>/", views.ThreadDetailView.as_view(), name="thread-detail"),
    path("<slug:thread_name>/join/", views.ThreadJoinView.as_view(), name="thread-join"),
    path(
        "<slug:thread_name>/update/",
        views.ThreadUpdateView.as_view(),
        name="thread-update",
    ),
    path(
        "<slug:thread_name>/delete/",
        views.ThreadDeleteView.as_view(),
        name="thread-delete",
    ),
]
