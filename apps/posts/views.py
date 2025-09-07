from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from apps.posts.models import Post
from apps.threads.models import Thread, ThreadMembership
from apps.campus.models import OrganizationMembership
from apps.votes.models import Vote
from apps.posts.forms import PostForm


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm

    def _get_requested_thread(self):
        thread_param = self.request.GET.get("thread")
        if not thread_param:
            return None
        if thread_param.isdigit():
            return Thread.objects.filter(pk=int(thread_param)).first()
        return Thread.objects.filter(slug=thread_param).first()

    def get_initial(self):
        initial = super().get_initial()
        thread = self._get_requested_thread()
        if thread:
            initial["thread"] = thread
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        thread = self._get_requested_thread()
        if thread:
            form.fields["thread"].queryset = Thread.objects.filter(pk=thread.pk)
            form.fields["thread"].empty_label = None
            form.fields["thread"].initial = thread
        else:
            user = self.request.user
            allowed_org_ids = OrganizationMembership.objects.filter(
                user=user, status="active"
            ).values_list("organization_id", flat=True)
            form.fields["thread"].queryset = Thread.objects.filter(
                organization_id__in=allowed_org_ids
            )
        return form

    def form_valid(self, form):
        user = self.request.user
        thread = form.cleaned_data.get("thread")

        # Check if thread and organization exist
        if not thread or not thread.organization:
            form.add_error(None, "Invalid thread selected.")
            return self.form_invalid(form)

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
    form_class = PostForm

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

    def dispatch(self, request, *args, **kwargs):
        """Check if user has permission to view this post"""
        post = self.get_object()
        if not post.can_user_view(request.user):
            from django.http import Http404

            raise Http404("Post not found or you don't have permission to view it.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Show only top-level comments here; replies are rendered recursively
        context["comments"] = self.object.comments.filter(parent__isnull=True).order_by(
            "-created_at"
        )
        # Sidebar data to match thread detail
        thread = self.object.thread
        context["thread"] = thread

        # Optimize queries by fetching all memberships at once
        memberships = (
            ThreadMembership.objects.select_related("user")
            .filter(thread=thread, status="active")
            .order_by("user__username")
        )

        context["member_count"] = memberships.count()
        context["admin_memberships"] = [m for m in memberships if m.role == "admin"]
        context["moderator_memberships"] = [
            m for m in memberships if m.role == "moderator"
        ]
        return context
