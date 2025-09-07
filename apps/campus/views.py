from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from apps.posts.models import Post
from apps.threads.models import Thread
from apps.campus.models import Organization, OrganizationMembership
from apps.accounts.models import User
from apps.campus.forms import OrganizationForm


def home(request):
    tab = request.GET.get("tab", "home")

    # Use the custom manager to filter posts based on user visibility
    queryset = Post.objects.visible_to_user(request.user)
    if tab == "popular":
        posts = queryset.order_by(
            "-upvotes",
            "downvotes",
            "-view_count",
            "-comment_count",
            "-created_at",
        )
    else:
        # 'home' and 'all' default ordering
        posts = queryset.order_by("-is_pinned", "-created_at")

    context = {"posts": posts, "active_tab": tab}
    return render(request, "campus/home.html", context)


def about(request):
    return render(request, "campus/about.html")


def search(request):
    if request.htmx:
        query = request.POST.get("query", "")
        print(f"Query: {query}")
        if query:
            # Search across multiple models
            from django.db.models import Q

            # Search posts
            posts = (
                Post.objects.visible_to_user(request.user)
                .filter(Q(title__icontains=query) | Q(content__icontains=query))
                .select_related("thread", "author", "thread__organization")
                .distinct()
            )[:5]  # Limit results for HTMX

            # Search threads
            threads = (
                Thread.objects.filter(
                    Q(title__icontains=query) | Q(description__icontains=query)
                )
                .select_related("organization", "created_by")
                .distinct()
            )[:5]

            # Search organizations
            organizations = (
                Organization.objects.filter(
                    Q(name__icontains=query) | Q(description__icontains=query)
                ).distinct()
            )[:5]

            # Search users
            users = (
                User.objects.filter(
                    Q(username__icontains=query)
                    | Q(first_name__icontains=query)
                    | Q(last_name__icontains=query)
                    | Q(student_id__icontains=query)
                ).distinct()
            )[:5]

            context = {
                "posts": posts,
                "threads": threads,
                "organizations": organizations,
                "users": users,
                "search_query": query,
                "is_htmx": True,
            }
            return render(request, "partials/_search_results.html", context)
        else:
            # Return empty results when query is empty
            return render(
                request,
                "partials/_search_results.html",
                {
                    "posts": [],
                    "threads": [],
                    "organizations": [],
                    "users": [],
                    "search_query": "",
                    "is_htmx": True,
                },
            )
    else:
        # Handle non-HTMX requests (e.g., direct URL access)
        query = request.GET.get("query", "")
        if query:
            # Search across multiple models
            from django.db.models import Q

            # Search posts
            posts = (
                Post.objects.visible_to_user(request.user)
                .filter(Q(title__icontains=query) | Q(content__icontains=query))
                .select_related("thread", "author", "thread__organization")
                .distinct()
            )

            # Search threads
            threads = (
                Thread.objects.filter(
                    Q(title__icontains=query) | Q(description__icontains=query)
                )
                .select_related("organization", "created_by")
                .distinct()
            )

            # Search organizations
            organizations = Organization.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            ).distinct()

            # Search users
            users = User.objects.filter(
                Q(username__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(student_id__icontains=query)
            ).distinct()

            context = {
                "posts": posts,
                "threads": threads,
                "organizations": organizations,
                "users": users,
                "search_query": query,
                "is_htmx": False,
            }
            return render(request, "campus/search.html", context)
        return redirect("campus-home")


class OrganizationListView(ListView):
    model = Organization
    paginate_by = 20
    context_object_name = "organizations"
    template_name = "campus/organization_list.html"


class OrganizationDetailView(DetailView):
    model = Organization
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "campus/organization_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        membership = None
        can_join = False
        is_member = False
        organization: Organization = self.object
        if self.request.user.is_authenticated:
            membership = OrganizationMembership.objects.filter(
                user=self.request.user, organization=organization
            ).first()
            # Allow join only if no record exists or user was previously inactive
            can_join = (
                membership is None or getattr(membership, "status", "") == "inactive"
            )
            is_member = bool(
                membership and getattr(membership, "status", "") == "active"
            )
        else:
            # Anonymous users can see join CTA (will be redirected to login by view)
            can_join = True
            is_member = False

        # Threads under this organization (always shown)
        threads = (
            Thread.objects.filter(organization=organization)
            .select_related("organization")
            .order_by("-is_pinned", "-updated_at")
        )

        # Posts from threads under this organization with sorting tabs
        # Only show posts to active members
        posts = Post.objects.none()  # Default to empty queryset
        if is_member:
            tab = self.request.GET.get("tab", "popular")
            posts_qs = Post.objects.visible_to_organization(
                organization
            ).select_related("thread", "author")
            if tab == "latest":
                posts = posts_qs.order_by("-is_pinned", "-created_at")
            else:  # popular (default)
                posts = posts_qs.order_by(
                    "-upvotes",
                    "downvotes",
                    "-view_count",
                    "-comment_count",
                    "-created_at",
                )

        # Leadership and staff groupings
        active_memberships = OrganizationMembership.objects.select_related(
            "user"
        ).filter(organization=organization, status="active")
        committee_roles = {"president", "vice_president", "secretary", "treasurer"}
        committee_memberships = active_memberships.filter(role__in=committee_roles)
        admin_memberships = active_memberships.filter(role="admin")
        moderator_memberships = active_memberships.filter(role="moderator")

        # Post count should only be shown to members
        post_count = 0
        if is_member:
            post_count = Post.objects.filter(thread__organization=organization).count()

        # Check staff permissions
        from .permissions import is_org_staff
        is_staff = is_org_staff(self.request.user, organization)

        # Get pending requests count for staff
        pending_requests_count = 0
        if is_staff:
            pending_requests_count = OrganizationMembership.objects.filter(
                organization=organization, status="pending"
            ).count()

        context.update(
            {
                "membership": membership,
                "can_join": can_join,
                "is_member": is_member,
                "is_staff": is_staff,
                "pending_requests_count": pending_requests_count,
                "threads": threads,
                "posts": posts,
                "active_tab": tab if is_member else "popular",
                "thread_count": threads.count(),
                "post_count": post_count,
                "committee_memberships": committee_memberships,
                "admin_memberships": admin_memberships,
                "moderator_memberships": moderator_memberships,
            }
        )
        return context


class OrganizationCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Organization
    form_class = OrganizationForm
    template_name = "campus/organization_form.html"

    def test_func(self):
        # Limit creation to verified users
        return getattr(self.request.user, "is_verified", False)

    def form_valid(self, form):
        response = super().form_valid(form)
        # Auto-subscribe creator as admin and set member_count
        OrganizationMembership.objects.get_or_create(
            user=self.request.user,
            organization=self.object,
            defaults={"role": "admin", "status": "active"},
        )
        if self.object.member_count == 0:
            self.object.member_count = 1
            self.object.save(update_fields=["member_count", "updated_at"])
        return response


class OrganizationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Organization
    form_class = OrganizationForm
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "campus/organization_form.html"

    def test_func(self):
        from .permissions import is_org_staff

        return is_org_staff(self.request.user, self.get_object())


class OrganizationMembershipCreateView(LoginRequiredMixin, CreateView):
    model = OrganizationMembership
    fields: list[str] = []
    template_name = "campus/org_join.html"

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug")
        try:
            organization = Organization.objects.get(slug=slug)
        except Organization.DoesNotExist:
            return render(request, "threads/thread_not_found.html", status=404)

        membership = OrganizationMembership.objects.filter(
            user=request.user, organization=organization
        ).first()
        if membership and membership.status in {"active", "pending", "banned"}:
            # Do not show join page if already active/pending/banned
            messages.info(
                request,
                "You're already associated with this organization."
                if membership.status != "banned"
                else "You are banned from this organization.",
            )
            return redirect(organization.get_absolute_url())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get("slug")
        try:
            organization = Organization.objects.get(slug=slug)
            context['organization'] = organization
        except Organization.DoesNotExist:
            pass
        return context

    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug")
        try:
            organization = Organization.objects.get(slug=slug)
        except Organization.DoesNotExist:
            return render(request, "threads/thread_not_found.html", status=404)

        membership, created = OrganizationMembership.objects.get_or_create(
            user=request.user,
            organization=organization,
            defaults={"role": "member", "status": "pending"},
        )

        if created:
            messages.success(request, "Join request submitted and pending approval.")
        else:
            if membership.status == "active":
                messages.info(
                    request, "You are already an active member of this organization."
                )
            elif membership.status == "pending":
                messages.info(request, "Your join request is already pending.")
            elif membership.status == "inactive":
                membership.status = "pending"
                membership.save(update_fields=["status", "updated_at"])
                messages.success(
                    request,
                    "Your membership request has been re-submitted for approval.",
                )
            elif membership.status == "banned":
                messages.error(request, "You are banned from this organization.")

        return redirect(organization.get_absolute_url())

    def get_success_url(self):
        return (
            self.object.organization.get_absolute_url()
            if hasattr(self.object.organization, "get_absolute_url")
            else "{}".format(self.request.META.get("HTTP_REFERER", "/"))
        )

    def get_initial(self):
        initial = super().get_initial()
        initial.update({"status": "pending"})
        return initial
