from django import template

from apps.campus.models import Organization
from apps.threads.models import Thread
from apps.posts.models import Post

register = template.Library()


@register.inclusion_tag("campus/_sidebar_organizations.html", takes_context=True)
def sidebar_organizations(context, limit: int = 10):
    organizations = Organization.objects.filter(is_active=True).order_by(
        "-member_count", "name"
    )[:limit]
    return {"organizations": organizations}


@register.inclusion_tag("campus/_sidebar_threads.html", takes_context=True)
def sidebar_threads(context, limit: int = 10):
    threads = Thread.objects.select_related("organization").order_by(
        "-is_pinned", "-updated_at"
    )[:limit]
    return {"threads": threads}


@register.inclusion_tag("campus/_sidebar_recent_posts.html", takes_context=True)
def sidebar_recent_posts(context, limit: int = 5):
    user = context.get("request").user if context.get("request") else None
    if user and user.is_authenticated:
        posts = (
            Post.objects.visible_to_user(user)
            .select_related("thread", "author")
            .order_by("-created_at")[:limit]
        )
    else:
        # For anonymous users, only show public posts
        posts = (
            Post.objects.filter(visibility="public")
            .select_related("thread", "author")
            .order_by("-created_at")[:limit]
        )
    return {"posts": posts}


@register.inclusion_tag("campus/_sidebar_popular_posts.html", takes_context=True)
def sidebar_popular_posts(context, limit: int = 5):
    user = context.get("request").user if context.get("request") else None
    if user and user.is_authenticated:
        posts = (
            Post.objects.visible_to_user(user)
            .select_related("thread", "author")
            .order_by(
                "-upvotes", "downvotes", "-view_count", "-comment_count", "-created_at"
            )[:limit]
        )
    else:
        # For anonymous users, only show public posts
        posts = (
            Post.objects.filter(visibility="public")
            .select_related("thread", "author")
            .order_by(
                "-upvotes", "downvotes", "-view_count", "-comment_count", "-created_at"
            )[:limit]
        )
    return {"posts": posts}
