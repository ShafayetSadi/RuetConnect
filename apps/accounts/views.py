from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.accounts.forms import (
    ProfileUpdateForm,
    UserUpdateForm,
    AvatarUpdateForm,
    PasswordChangeForm,
)


@login_required
def profile(request):
    posts = request.user.posts.all().order_by("-date_posted")
    context = {"posts": posts}
    return render(request, "account/profile.html", context)


@login_required
def profile_update(request):
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
                return redirect("profile")

        elif form_type == "profile_info":
            profile_form = ProfileUpdateForm(
                request.POST, instance=request.user.profile
            )
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile information updated successfully!")
                return redirect("profile")

        elif form_type == "avatar_update":
            avatar_form = AvatarUpdateForm(
                request.POST, request.FILES, instance=request.user.profile
            )
            if avatar_form.is_valid():
                avatar_form.save()
                messages.success(request, "Avatar updated successfully!")
                return redirect("profile")

        elif form_type == "password_change":
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Password changed successfully!")
                return redirect("profile")

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
