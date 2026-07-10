from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from accounts.models import Master

from .forms import AppointmentForm
from .services import get_available_slots, create_appointment


@login_required
def available_slots_view(request):
    master_id = request.GET.get("master_id")
    date_str = request.GET.get("date")
    duration = request.GET.get("duration")

    if not (master_id and date_str and duration):
        return JsonResponse({"error": "Missing parameters"}, status=400)

    try:
        master = Master.objects.get(pk=master_id)
    except Master.DoesNotExist:
        return JsonResponse({"error": "Master not found"}, status=404)

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        duration = int(duration)
    except ValueError:
        return JsonResponse({"error": "Invalid date or duration format"}, status=400)

    slots = get_available_slots(master, date, duration)

    return JsonResponse(
        {
            "slots": [
                {
                    "start": timezone.localtime(start).strftime("%H:%M"),
                    "end": timezone.localtime(end).strftime("%H:%M"),
                    "value": start.isoformat(),
                }
                for start, end in slots
            ]
        }
    )


@login_required
def booking_create_view(request):
    today = timezone.localdate()

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            create_appointment(
                client=request.user,
                master=form.cleaned_data["master"],
                service_list=form.cleaned_data["services"],
                start_at=form.cleaned_data["start_at"],
            )
            return redirect("home")
        return render(request, "booking/create.html", {"form": form, "today": today})

    return render(
        request, "booking/create.html", {"form": AppointmentForm(), "today": today}
    )
