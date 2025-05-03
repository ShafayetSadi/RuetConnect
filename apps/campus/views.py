from django.shortcuts import render

from apps.posts.models import Post

# Create your views here.


def home(request):
    posts = Post.objects.all().order_by("-date_posted")
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
