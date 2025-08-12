from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from apps.posts.models import Post
from apps.campus.models import Organization, OrganizationMembership
from apps.campus.forms import OrganizationForm, OrganizationMembershipForm

# Create your views here.


def home(request):
    posts = Post.objects.all().order_by("-created_at")
    context = {"posts": posts}
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


class OrganizationDetailView(DetailView):
    model = Organization
    slug_field = "slug"
    slug_url_kwarg = "slug"


class OrganizationCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Organization
    form_class = OrganizationForm

    def test_func(self):
        # Limit creation to verified users
        return getattr(self.request.user, "is_verified", False)


class OrganizationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Organization
    form_class = OrganizationForm
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def test_func(self):
        # Allow org editors later; for now only staff can edit
        return self.request.user.is_staff


class OrganizationMembershipCreateView(LoginRequiredMixin, CreateView):
    model = OrganizationMembership
    form_class = OrganizationMembershipForm

    def form_valid(self, form):
        form.save(user=self.request.user)
        return super().form_valid(form)
