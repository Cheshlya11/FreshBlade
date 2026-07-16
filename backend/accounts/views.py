from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth.forms import AuthenticationForm

from .forms import (
    ClientRegistrationForm,
    ProfileEditForm,
    MasterUserForm,
    MasterProfileForm,
)

from .models import Master, User
from booking.models import MasterSchedule


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


@login_required
def profile_edit_view(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("accounts:profile")
        return render(request, "accounts/profile_edit.html", {"form": form})

    return render(
        request,
        "accounts/profile_edit.html",
        {"form": ProfileEditForm(instance=request.user)},
    )


@staff_member_required
def master_create_view(request):
    if request.method == "POST":
        user_form = MasterUserForm(request.POST)
        master_form = MasterProfileForm(request.POST)
        if user_form.is_valid() and master_form.is_valid():
            user = User.objects.create_user(
                email=user_form.cleaned_data["email"],
                first_name=user_form.cleaned_data["first_name"],
                last_name=user_form.cleaned_data["last_name"],
                phone=user_form.cleaned_data["phone"],
                password=user_form.cleaned_data["password"],
                role="MASTER",
            )

            master = master_form.save(commit=False)
            master.user = user
            master.save()

            return redirect("accounts:master_schedule_create", master_id=master.user.id)
    else:
        user_form = MasterUserForm()
        master_form = MasterProfileForm()

    return render(
        request,
        "accounts/master_create.html",
        {
            "user_form": user_form,
            "master_form": master_form,
        },
    )


@staff_member_required
def master_schedule_create_view(request, master_id):
    master = get_object_or_404(Master, pk=master_id)
    weekdays = MasterSchedule.Weekday.choices
    errors = []

    if request.method == "POST":
        if "skip" in request.POST:
            return redirect("catalog:master_list")

        schedule_entries = []
        for value, label in weekdays:
            start = request.POST.get(f"start_{value}")
            end = request.POST.get(f"end_{value}")
            if start and end:
                if start >= end:
                    errors.append(f"{label}: start time must be before end time.")
                else:
                    schedule_entries.append((value, start, end))

        if not errors:
            for value, start, end in schedule_entries:
                MasterSchedule.objects.create(
                    master=master, weekday=value, start_time=start, end_time=end
                )
            return redirect("catalog:master_list")

    return render(
        request,
        "accounts/master_schedule_create.html",
        {
            "master": master,
            "weekdays": weekdays,
            "errors": errors,
        },
    )
