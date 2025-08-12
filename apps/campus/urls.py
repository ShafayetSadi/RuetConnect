from django.urls import path

from .views import (
    OrganizationCreateView,
    OrganizationDetailView,
    OrganizationListView,
    OrganizationMembershipCreateView,
    OrganizationUpdateView,
    about,
    home,
    search,
)

urlpatterns = [
    path("", home, name="campus-home"),
    path("about/", about, name="campus-about"),
    path("search/", search, name="campus-search"),
    path("orgs/", OrganizationListView.as_view(), name="org-list"),
    path("orgs/create/", OrganizationCreateView.as_view(), name="org-create"),
    path("orgs/<slug:slug>/", OrganizationDetailView.as_view(), name="org-detail"),
    path(
        "orgs/<slug:slug>/edit/",
        OrganizationUpdateView.as_view(),
        name="org-edit",
    ),
    path(
        "orgs/<slug:slug>/join/",
        OrganizationMembershipCreateView.as_view(),
        name="org-join",
    ),
]
