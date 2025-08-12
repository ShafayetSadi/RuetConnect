from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from apps.posts.models import Post
from apps.threads.models import ThreadMembership
from apps.campus.models import OrganizationMembership


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ["thread", "title", "content"]

    def form_valid(self, form):
        user = self.request.user
        thread = form.cleaned_data.get("thread")
        # Require org membership and thread membership
        if not OrganizationMembership.objects.filter(
            organization=thread.organization, user=user, status="active"
        ).exists():
            form.add_error(None, "You must be a member of the organization to post.")
            return self.form_invalid(form)
        if not ThreadMembership.objects.filter(
            thread=thread, user=user, status="active"
        ).exists():
            form.add_error(None, "You must join this thread to post.")
            return self.form_invalid(form)

        form.instance.author = user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ["title", "content"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = "/"

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = self.object.comments.all().order_by("-created_at")
        return context
