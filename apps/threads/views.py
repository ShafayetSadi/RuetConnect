from django.views.generic import TemplateView
from apps.campus.models import Organization, OrganizationMembership
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from .forms import ThreadForm
from .models import Thread, ThreadMembership
from apps.campus.models import OrganizationMembership
from apps.posts.models import Post

class ThreadOrgSelectView(LoginRequiredMixin, TemplateView):
    template_name = "threads/thread_select_org.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Show only organizations the user is a member of
        orgs = Organization.objects.filter(
            organizationmembership__user=self.request.user,
            organizationmembership__status="active"
        ).distinct()
        context["organizations"] = orgs
        return context

class ThreadDetailView(DetailView):
    model = Thread
    slug_field = "slug"
    slug_url_kwarg = "thread_name"

    def get(self, request, *args, **kwargs):
        try:
            response = super().get(request, *args, **kwargs)
        except Http404:
            return render(request, "threads/thread_not_found.html", status=404)

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        thread = self.object
        user = self.request.user
        is_org_member = False
        is_thread_member = False
        can_join_org = False
        can_join_thread = False

        if user.is_authenticated:
            is_org_member = OrganizationMembership.objects.filter(
                organization=thread.organization, user=user, status="active"
            ).exists()
            is_thread_member = ThreadMembership.objects.filter(
                thread=thread, user=user, status="active"
            ).exists()

            # Determine if user can join organization or thread
            if not is_org_member:
                # Check if user can join the organization
                org_membership = OrganizationMembership.objects.filter(
                    organization=thread.organization, user=user
                ).first()
                can_join_org = (
                    org_membership is None or org_membership.status == "inactive"
                )
            elif is_org_member and not is_thread_member:
                # User is org member but not thread member - can join thread
                can_join_thread = True
        else:
            # Anonymous users can see the visitor page
            can_join_org = True

        # Only show posts and full content to thread members
        posts = []
        tab = "popular"
        if is_thread_member:
            tab = self.request.GET.get("tab", "popular")
            # Only show posts in this thread
            posts_qs = Post.objects.filter(thread=thread).select_related("thread", "author")
            if tab == "latest":
                posts = posts_qs.order_by("-is_pinned", "-created_at")
            else:
                posts = posts_qs.order_by(
                    "-upvotes",
                    "downvotes",
                    "-view_count",
                    "-comment_count",
                    "-created_at",
                )

        # Sidebar data: admins, moderators, member count
        admin_memberships = (
            ThreadMembership.objects.select_related("user")
            .filter(thread=thread, status="active", role="admin")
            .order_by("user__username")
        )
        moderator_memberships = (
            ThreadMembership.objects.select_related("user")
            .filter(thread=thread, status="active", role="moderator")
            .order_by("user__username")
        )
        member_count = ThreadMembership.objects.filter(
            thread=thread, status="active"
        ).count()

        context.update(
            {
                "is_org_member": is_org_member,
                "is_thread_member": is_thread_member,
                "can_join_org": can_join_org,
                "can_join_thread": can_join_thread,
                "posts": posts,
                "active_tab": tab,
                "admin_memberships": admin_memberships,
                "moderator_memberships": moderator_memberships,
                "member_count": member_count,
            }
        )
        return context


class ThreadCreateView(LoginRequiredMixin, CreateView):
    model = Thread
    form_class = ThreadForm
    template_name = 'threads/thread_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        org_slug = self.kwargs.get('org_slug')
        if org_slug:
            from apps.campus.models import Organization
            try:
                organization = Organization.objects.get(slug=org_slug)
                kwargs['initial'] = kwargs.get('initial', {})
                kwargs['initial']['organization'] = organization
            except Organization.DoesNotExist:
                pass
        return kwargs
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        # Set organization from org_slug
        org_slug = self.kwargs.get('org_slug')
        if org_slug:
            from apps.campus.models import Organization
            try:
                organization = Organization.objects.get(slug=org_slug)
                form.instance.organization = organization
            except Organization.DoesNotExist:
                pass
        response = super().form_valid(form)
        # Ensure creator becomes thread admin with active status
        ThreadMembership.objects.get_or_create(
            thread=self.object,
            user=self.request.user,
            defaults={"status": "active", "role": "admin"},
        )
        return response


class ThreadJoinView(LoginRequiredMixin, DetailView):
    model = Thread
    slug_field = "slug"
    slug_url_kwarg = "thread_name"
    template_name = "threads/thread_join.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Check org membership first
        if not OrganizationMembership.objects.filter(
            organization=self.object.organization, user=request.user, status="active"
        ).exists():
            # Redirect to thread detail view which will show appropriate visitor page
            return redirect(self.object.get_absolute_url())

        membership, created = ThreadMembership.objects.get_or_create(
            thread=self.object,
            user=request.user,
            defaults={"status": "active", "role": "member"},
        )
        if not created and membership.status != "active":
            membership.status = "active"
            membership.save(update_fields=["status", "updated_at"])
        # Redirect to thread detail after joining
        return redirect(self.object.get_absolute_url())


class ThreadUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Thread
    form_class = ThreadForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def test_func(self):
        thread = self.get_object()
        return self.request.user == thread.created_by


class ThreadDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Thread
    success_url = "/"

    def test_func(self):
        thread = self.get_object()
        return self.request.user == thread.created_by
