from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from apps.accounts.forms import (
    ProfileUpdateForm,
    UserUpdateForm,
    AvatarUpdateForm,
    PasswordChangeForm,
)
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from typing import Dict, Any

from apps.votes.models import Vote
from apps.posts.models import Post
from apps.comments.models import Comment

User = get_user_model()


def _get_profile_user(username: str) -> User:
    return get_object_or_404(User, username=username)


def _get_base_stats(profile_user: User) -> Dict[str, int]:
    """Return common counters used in profile side bar."""
    return {
        "total_posts": Post.objects.filter(author=profile_user, is_deleted=False).count(),
        "total_comments": Comment.objects.filter(author=profile_user, is_deleted=False).count(),
        "total_upvotes_given": Vote.objects.filter(user=profile_user, vote_type=1).count(),
    }


def user_detail(request: HttpRequest, username: str) -> HttpResponseRedirect:
    """Legacy route kept for backward compatibility -> redirect to posts section."""
    return HttpResponseRedirect(reverse("user-posts", kwargs={"username": username}))


def user_posts(request: HttpRequest, username: str) -> HttpResponse:
    profile_user = _get_profile_user(username)
    # Filter posts by author's posts BUT enforce viewer visibility rules
    visible_posts = Post.objects.visible_to_user(request.user).filter(author=profile_user, is_deleted=False).order_by("-created_at")
    context: Dict[str, Any] = {
        "profile_user": profile_user,
        "posts": visible_posts,
        "section": "posts",
        **_get_base_stats(profile_user),
    }
    return render(request, "account/profile_posts.html", context)


def user_comments(request: HttpRequest, username: str) -> HttpResponse:
    profile_user = _get_profile_user(username)
    # Show comments the profile_user made on posts the current viewer can see
    visible_post_ids = Post.objects.visible_to_user(request.user).values_list("id", flat=True)
    comments = (
        Comment.objects.filter(author=profile_user, post_id__in=visible_post_ids, is_deleted=False)
        .select_related("post", "author")
        .order_by("-created_at")
    )
    context: Dict[str, Any] = {
        "profile_user": profile_user,
        "comments": comments,
        "section": "comments",
        **_get_base_stats(profile_user),
    }
    return render(request, "account/profile_comments.html", context)


def user_upvoted(request: HttpRequest, username: str) -> HttpResponse:
    profile_user = _get_profile_user(username)
    post_ct = ContentType.objects.get_for_model(Post)
    upvote_ids = (
        Vote.objects.filter(user=profile_user, vote_type=1, content_type=post_ct)
        .order_by("-created_at")
        .values_list("object_id", flat=True)
    )
    posts = Post.objects.visible_to_user(request.user).filter(id__in=upvote_ids, is_deleted=False).order_by("-created_at")
    context: Dict[str, Any] = {
        "profile_user": profile_user,
        "upvoted_posts": posts,
        "section": "upvoted",
        **_get_base_stats(profile_user),
    }
    return render(request, "account/profile_upvoted.html", context)


def user_downvoted(request: HttpRequest, username: str) -> HttpResponse:
    profile_user = _get_profile_user(username)
    post_ct = ContentType.objects.get_for_model(Post)
    downvote_ids = (
        Vote.objects.filter(user=profile_user, vote_type=-1, content_type=post_ct)
        .order_by("-created_at")
        .values_list("object_id", flat=True)
    )
    posts = Post.objects.visible_to_user(request.user).filter(id__in=downvote_ids, is_deleted=False).order_by("-created_at")
    context: Dict[str, Any] = {
        "profile_user": profile_user,
        "downvoted_posts": posts,
        "section": "downvoted",
        **_get_base_stats(profile_user),
    }
    return render(request, "account/profile_downvoted.html", context)


@login_required
def user_update(request):
    """Edit user profile with multiple forms"""
    user_form = UserUpdateForm(instance=request.user)
    profile_form = ProfileUpdateForm(instance=request.user.profile)
    avatar_form = AvatarUpdateForm(instance=request.user.profile)
    password_form = PasswordChangeForm(user=request.user)

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "user_info":
            user_form = UserUpdateForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect("user-posts", username=request.user.username)

        elif form_type == "profile_info":
            profile_form = ProfileUpdateForm(
                request.POST, instance=request.user.profile
            )
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile information updated successfully!")
                return redirect("user-posts", username=request.user.username)

        elif form_type == "avatar_update":
            avatar_form = AvatarUpdateForm(
                request.POST, request.FILES, instance=request.user.profile
            )
            if avatar_form.is_valid():
                avatar_form.save()
                messages.success(request, "Avatar updated successfully!")
                return redirect("user-posts", username=request.user.username)

        elif form_type == "password_change":
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Password changed successfully!")
                return redirect("user-posts", username=request.user.username)

    return render(
        request,
        "account/profile_update.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "avatar_form": avatar_form,
            "password_form": password_form,
        },
    )


@login_required
@require_http_methods(["POST"])
def avatar_update(request):
    """HTMX endpoint for avatar updates"""
    form = AvatarUpdateForm(request.POST, request.FILES, instance=request.user.profile)

    if form.is_valid():
        form.save()
        return render(
            request,
            "users/partials/avatar_preview.html",
            {"user": request.user},
        )
    else:
        return render(
            request,
            "users/partials/avatar_form.html",
            {"avatar_form": form},
        )
