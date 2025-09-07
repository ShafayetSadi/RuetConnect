from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView
from django.shortcuts import get_object_or_404

from apps.posts.models import Post

from .models import Comment

# Create your views here.


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ["content"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        post = get_object_or_404(Post, slug=self.kwargs["slug"])
        form.instance.post = post
        parent_id = self.request.POST.get("parent_id")
        if parent_id:
            try:
                form.instance.parent = Comment.objects.get(pk=int(parent_id), post=post)
            except (ValueError, Comment.DoesNotExist):
                pass
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        post = Post.objects.get(slug=self.kwargs["slug"])
        context = self.get_context_data(form=form, post=post)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post"] = Post.objects.get(slug=self.kwargs["slug"])
        return context

    def get_success_url(self):
        return reverse("post-detail", kwargs={"slug": self.object.post.slug})
