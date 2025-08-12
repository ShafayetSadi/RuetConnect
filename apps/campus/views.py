from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from apps.posts.models import Post
from apps.campus.models import Organization, OrganizationMembership
from apps.campus.forms import OrganizationForm, OrganizationMembershipForm

# Create your views here.


def home(request):
    tab = request.GET.get("tab", "home")

    queryset = Post.objects.all()
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
            posts = Post.objects.filter(title__icontains=query)
            context = {"posts": posts}
            return render(request, "campus/partials/_search_results.html", context)
        print("No query")
    else:
        print("Not htmx")
    return render(request, "campus/home.html")


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
        if self.request.user.is_authenticated:
            membership = OrganizationMembership.objects.filter(
                user=self.request.user, organization=self.object
            ).first()
            # Allow join only if no record exists or user was previously inactive
            can_join = membership is None or getattr(membership, "status", "") == "inactive"
        else:
            # Anonymous users can see join CTA (will be redirected to login by view)
            can_join = True
        context.update({
            "membership": membership,
            "can_join": can_join,
        })
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
                "You're already associated with this organization." if membership.status != "banned" else "You are banned from this organization.",
            )
            return redirect(organization.get_absolute_url())
        return super().get(request, *args, **kwargs)

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
                messages.info(request, "You are already an active member of this organization.")
            elif membership.status == "pending":
                messages.info(request, "Your join request is already pending.")
            elif membership.status == "inactive":
                membership.status = "pending"
                membership.save(update_fields=["status", "updated_at"])
                messages.success(request, "Your membership request has been re-submitted for approval.")
            elif membership.status == "banned":
                messages.error(request, "You are banned from this organization.")

        return redirect(organization.get_absolute_url())

    def get_success_url(self):
        return self.object.organization.get_absolute_url() if hasattr(self.object.organization, "get_absolute_url") else \
            "{}".format(self.request.META.get("HTTP_REFERER", "/"))

    def get_initial(self):
        initial = super().get_initial()
        initial.update({"status": "pending"})
        return initial
