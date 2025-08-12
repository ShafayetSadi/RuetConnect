from django import template

from apps.campus.models import Organization
from apps.threads.models import Thread
from apps.posts.models import Post

register = template.Library()


@register.inclusion_tag("campus/_sidebar_organizations.html", takes_context=True)
def sidebar_organizations(context, limit: int = 10):
    organizations = (
        Organization.objects.filter(is_active=True)
        .order_by("-member_count", "name")[:limit]
    )
    return {"organizations": organizations}


@register.inclusion_tag("campus/_sidebar_threads.html", takes_context=True)
def sidebar_threads(context, limit: int = 10):
    threads = (
        Thread.objects.select_related("organization")
        .order_by("-is_pinned", "-updated_at")[:limit]
    )
    return {"threads": threads}


@register.inclusion_tag("campus/_sidebar_recent_posts.html", takes_context=True)
def sidebar_recent_posts(context, limit: int = 5):
    posts = (
        Post.objects.select_related("thread", "author")
        .order_by("-created_at")[:limit]
    )
    return {"posts": posts}


@register.inclusion_tag("campus/_sidebar_popular_posts.html", takes_context=True)
def sidebar_popular_posts(context, limit: int = 5):
    posts = (
        Post.objects.select_related("thread", "author")
        .order_by("-upvotes", "downvotes", "-view_count", "-comment_count", "-created_at")[:limit]
    )
    return {"posts": posts}
