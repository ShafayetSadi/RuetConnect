from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.shortcuts import render
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from .models import Thread, ThreadMembership
from apps.campus.models import OrganizationMembership


class ThreadDetailView(DetailView):
    model = Thread
    slug_field = "slug"
    slug_url_kwarg = "thread_name"

    def get(self, request, *args, **kwargs):
        try:
            response = super().get(request, *args, **kwargs)
        except Http404:
            return render(request, "threads/thread_not_found.html", status=404)

        # Enforce membership: user must be org member and thread member
        thread = self.object
        user = request.user
        if not user.is_authenticated:
            return render(request, "threads/thread_not_found.html", status=403)

        org_member = OrganizationMembership.objects.filter(
            organization=thread.organization, user=user, status="active"
        ).exists()
        if not org_member:
            return render(request, "threads/thread_not_found.html", status=403)

        thread_member = ThreadMembership.objects.filter(
            thread=thread, user=user, status="active"
        ).exists()
        if not thread_member:
            return render(request, "threads/thread_join_required.html", {"thread": thread}, status=403)

        return response


class ThreadCreateView(LoginRequiredMixin, CreateView):
    model = Thread
    fields = ["title", "description", "thread_type", "organization"]

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


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
            return render(request, "threads/thread_join_required.html", {"thread": self.object}, status=403)

        ThreadMembership.objects.get_or_create(
            thread=self.object, user=request.user, defaults={"status": "active"}
        )
        return render(request, "threads/thread_detail.html", {"thread": self.object})


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
