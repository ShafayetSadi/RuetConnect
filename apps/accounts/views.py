from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.accounts.forms import UpdateProfileForm, UserUpdateForm


@login_required
def profile(request):
    posts = request.user.posts.all().order_by("-date_posted")
    context = {"posts": posts}
    return render(request, "accounts/profile.html", context)


@login_required
def profile_update(request):
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("profile")
        else:
            messages.error(request, "Profile update failed. Invalid information.")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    context = {"user_form": user_form, "profile_form": profile_form}
    return render(request, "accounts/profile_update.html", context)
