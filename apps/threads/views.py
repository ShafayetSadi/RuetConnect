from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.shortcuts import render
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from .models import Thread


class ThreadDetailView(DetailView):
    model = Thread
    slug_field = "slug"
    slug_url_kwarg = "thread_name"

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return render(request, "threads/thread_not_found.html", status=404)


class ThreadCreateView(LoginRequiredMixin, CreateView):
    model = Thread
    fields = ["title", "description", "thread_type", "organization"]

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ThreadUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Thread
    fields = ["title", "description", "thread_type", "is_pinned", "is_locked"]

    def test_func(self):
        thread = self.get_object()
        return self.request.user == thread.created_by


class ThreadDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Thread
    success_url = "/"

    def test_func(self):
        thread = self.get_object()
        return self.request.user == thread.created_by
