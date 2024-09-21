from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect

from users.forms import CreateUserForm, UpdateProfileForm, UpdateUserForm


# Create your views here.

def register(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            login(request)
            messages.success(request, 'Account created successfully')
            return redirect('login')
        messages.error(request, 'Account creation failed. Invalid information.')
    else:
        form = CreateUserForm()
    return render(request, 'users/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('campus-home')
        else:
            messages.error(request, 'Username or password is incorrect')
    else:
        form = AuthenticationForm()
    context = {'form': form}
    return render(request, 'users/login.html', context)


def logout(request):
    auth_logout(request)
    return render(request, 'users/logout.html')


@login_required
def profile(request):
    posts = request.user.posts.all().order_by('-date_posted')
    context = {'posts': posts}
    return render(request, 'users/profile.html', context)


@login_required
def profile_update(request):
    if request.method == 'POST':
        u_form = UpdateUserForm(request.POST, instance=request.user)
        p_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            print(p_form)
            u_form.save()
            p_form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
        print(u_form.errors)
        print(p_form.errors)
        messages.error(request, 'Profile update failed. Invalid information.')
    else:
        u_form = UpdateUserForm(instance=request.user)
        p_form = UpdateProfileForm(instance=request.user.profile)
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile_update.html', context)
