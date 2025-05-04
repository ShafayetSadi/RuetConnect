from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.accounts.forms import UpdateProfileForm


@login_required
def profile(request):
    posts = request.user.posts.all().order_by("-date_posted")
    context = {"posts": posts}
    return render(request, "accounts/profile.html", context)


@login_required
def profile_update(request):
    if request.method == "POST":
        p_form = UpdateProfileForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        messages.error(request, "Profile update failed. Invalid information.")
    else:
        p_form = UpdateProfileForm(instance=request.user.profile)
    context = {"p_form": p_form}
    return render(request, "accounts/profile_update.html", context)
