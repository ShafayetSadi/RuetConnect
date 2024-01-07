from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect

from users.forms import CreateUserForm


# Create your views here.

def register(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully')
            return redirect('campus-home')
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
    return redirect('campus-home')