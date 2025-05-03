from django.http import Http404, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from .models import Thread


# Create your views here.
def thread(request, thread_name):
    try:
        thread = get_object_or_404(Thread, name=thread_name)
        contex = {"thread": thread}
        return render(request, "threads/thread.html", contex)
    except Http404:
        return HttpResponseNotFound("<h1>Thread not found</h1>")


class ThreadDetailView(DetailView):
    model = Thread
    slug_field = "name"
    slug_url_kwarg = "thread_name"

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except Http404:
            return None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            return render(request, "threads/thread_not_found.html", status=404)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class ThreadCreateView(CreateView):
    model = Thread
    fields = ["name", "description"]

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("campus-home")


class ThreadUpdateView(UpdateView):
    model = Thread
    fields = ["name", "title", "description", "image", "banner"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        thread = self.get_object()
        if self.request.user == thread.author:
            return True
        return False


class ThreadDeleteView(DeleteView):
    model = Thread
    success_url = "/"

    def test_func(self):
        thread = self.get_object()
        if self.request.user == thread.author:
            return True
        return False
