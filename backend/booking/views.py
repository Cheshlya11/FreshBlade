from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator

from accounts.models import Master

from .models import Appointment
from .forms import AppointmentForm, AppointmentFilterForm
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


@login_required
def my_appointments_view(request):
    if request.user.is_staff:
        return redirect("/admin/booking/appointment/")

    has_completable = False

    if request.user.role == "MASTER":
        appointments = Appointment.objects.filter(master=request.user.master_profile)
        has_completable = Appointment.objects.filter(
            master=request.user.master_profile,
            status=Appointment.Status.CONFIRMED,
            start_at__lt=timezone.now(),
        ).exists()
    else:
        appointments = Appointment.objects.filter(client=request.user)

    form = AppointmentFilterForm(request.GET, user=request.user)

    status = request.GET.get("status", "CONFIRMED")
    appointments = appointments.filter(status=status)

    if form.is_valid():
        master = form.cleaned_data.get("master")
        if master:
            appointments = appointments.filter(master=master)

        search = form.cleaned_data.get("search")
        if search:
            appointments = appointments.filter(
                Q(client__first_name__icontains=search)
                | Q(client__last_name__icontains=search)
                | Q(client__email__icontains=search)
            )

        date_from = form.cleaned_data.get("date_from")
        if date_from:
            appointments = appointments.filter(start_at__date__gte=date_from)

        date_to = form.cleaned_data.get("date_to")
        if date_to:
            appointments = appointments.filter(start_at__date__lte=date_to)

        appointments = appointments.order_by(
            "-start_at" if status == "COMPLETED" else "start_at"
        )

    paginator = Paginator(appointments, 6)
    page_obj = paginator.get_page(request.GET.get("page"))

    for appointment in page_obj:
        appointment.can_complete = (
            appointment.status == Appointment.Status.CONFIRMED
            and appointment.start_at < timezone.now()
        )
        appointment.total_price = sum(
            s.price_at_booking for s in appointment.appointmentservice_set.all()
        )

    query_params = request.GET.copy()
    query_params.pop("page", None)

    return render(
        request,
        "booking/my-appointments.html",
        {
            "form": form,
            "page_obj": page_obj,
            "status": status,
            "query_params": query_params.urlencode(),
            "has_completable": has_completable,
        },
    )


@login_required
def cancel_appointment_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)

    is_owner = (
        request.user.role == "CLIENT" and appointment.client == request.user
    ) or (
        request.user.role == "MASTER"
        and appointment.master == request.user.master_profile
    )
    if not is_owner:
        return redirect("booking:my_appointments")

    if appointment.status == Appointment.Status.CONFIRMED:
        appointment.status = Appointment.Status.CANCELLED
        appointment.save()

    return redirect("booking:my_appointments")


@login_required
def complete_appointment_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)

    is_master = (
        request.user.role == "MASTER"
        and appointment.master == request.user.master_profile
    )
    if not is_master:
        return redirect("booking:my_appointments")

    if (
        appointment.status == Appointment.Status.CONFIRMED
        and appointment.start_at < timezone.now()
    ):
        appointment.status = Appointment.Status.COMPLETED
        appointment.save()

    return redirect("booking:my_appointments")


@require_POST
@login_required
def complete_all_appointments_view(request):
    if request.user.role != "MASTER":
        return redirect("booking:my_appointments")

    Appointment.objects.filter(
        master=request.user.master_profile,
        status=Appointment.Status.CONFIRMED,
        start_at__lt=timezone.now(),
    ).update(status=Appointment.Status.COMPLETED)

    return redirect(f"{reverse('booking:my_appointments')}?status=CONFIRMED")
