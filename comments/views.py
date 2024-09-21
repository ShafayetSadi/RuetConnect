from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from .models import Comment
from posts.models import Post


# Create your views here.


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = Post.objects.get(slug=self.kwargs['slug'])
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        post = Post.objects.get(slug=self.kwargs['slug'])
        context = self.get_context_data(form=form, post=post)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = Post.objects.get(slug=self.kwargs['slug'])
        return context

    def get_success_url(self):
        return reverse('post-detail', kwargs={'slug': self.object.post.slug})

