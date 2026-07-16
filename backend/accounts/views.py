from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required

from django.contrib.auth.forms import AuthenticationForm

from .forms import ClientRegistrationForm


def register_view(request):
    if request.method == "POST":
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = user.Role.CLIENT
            user.save()
            auth_login(request, user)
            return redirect("pages:home")
        return render(request, "accounts/register.html", {"form": form})

    return render(request, "accounts/register.html", {"form": ClientRegistrationForm()})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect("pages:home")
        return render(request, "accounts/login.html", {"form": form})

    return render(request, "accounts/login.html", {"form": AuthenticationForm})


def logout_view(request):
    auth_logout(request)
    return redirect("accounts:login")


@login_required
def profile_view(request):
    display_role = "ADMIN" if request.user.is_staff else request.user.role

    context = {
        "display_role": display_role,
    }
    return render(request, "accounts/profile.html", context)
