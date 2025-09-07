from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, UpdateView, View
from django.http import JsonResponse

from apps.campus.models import Organization, OrganizationMembership
from apps.campus.permissions import is_org_staff


class OrganizationPendingRequestsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = "campus/org_pending_requests.html"
    context_object_name = "pending_requests"
    paginate_by = 25

    def get_org(self) -> Organization:
        return get_object_or_404(Organization, slug=self.kwargs["slug"])

    def test_func(self) -> bool:
        return is_org_staff(self.request.user, self.get_org())

    def get_queryset(self):
        return (
            OrganizationMembership.objects.select_related("user")
            .filter(organization=self.get_org(), status="pending")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["organization"] = self.get_org()
        return ctx


class OrganizationMembershipActionView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get_org(self) -> Organization:
        return get_object_or_404(Organization, slug=self.kwargs["slug"])

    def test_func(self) -> bool:
        return is_org_staff(self.request.user, self.get_org())

    def post(self, request, *args, **kwargs):
        organization = self.get_org()
        membership_id = kwargs.get("membership_id")
        action = request.POST.get("action")

        membership = get_object_or_404(
            OrganizationMembership,
            pk=membership_id,
            organization=organization,
            status="pending"
        )

        if action == "approve":
            membership.status = "active"
            membership.save(update_fields=["status", "updated_at"])
            # Update member count
            organization.member_count = OrganizationMembership.objects.filter(
                organization=organization, status="active"
            ).count()
            organization.save(update_fields=["member_count", "updated_at"])
            messages.success(request, f"Approved {membership.user.username}'s membership request.")
        elif action == "reject":
            membership.delete()
            messages.success(request, f"Rejected {membership.user.username}'s membership request.")
        else:
            messages.error(request, "Invalid action.")

        return redirect("org-pending-requests", slug=organization.slug)


class OrganizationMembersListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = "campus/org_members.html"
    context_object_name = "memberships"
    paginate_by = 25

    def get_org(self) -> Organization:
        return get_object_or_404(Organization, slug=self.kwargs["slug"])

    def test_func(self) -> bool:
        return is_org_staff(self.request.user, self.get_org())

    def get_queryset(self):
        return (
            OrganizationMembership.objects.select_related("user", "organization")
            .filter(organization=self.get_org())
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["organization"] = self.get_org()
        return ctx


class OrganizationMembershipUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = OrganizationMembership
    fields = ["role", "status"]
    template_name = "campus/org_membership_form.html"
    pk_url_kwarg = "membership_id"

    def get_org(self) -> Organization:
        return get_object_or_404(Organization, slug=self.kwargs["slug"])

    def get_object(self, queryset=None):
        return get_object_or_404(
            OrganizationMembership, pk=self.kwargs["membership_id"], organization=self.get_org()
        )

    def test_func(self) -> bool:
        return is_org_staff(self.request.user, self.get_org())

    def get_success_url(self):
        messages.success(self.request, "Membership updated.")
        return reverse("org-members", kwargs={"slug": self.kwargs["slug"]})
