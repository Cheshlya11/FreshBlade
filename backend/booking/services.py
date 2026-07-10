from datetime import timedelta
from django.utils import timezone

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import MasterSchedule, Appointment, AppointmentService


def get_available_slots(master, date, duration_minutes, step_minutes=30):
    weekday = date.isoweekday()

    schedule = MasterSchedule.objects.filter(master=master, weekday=weekday).first()
    if schedule is None:
        return []

    work_start = timezone.make_aware(timezone.datetime.combine(date, schedule.start_time))
    work_end = timezone.make_aware(timezone.datetime.combine(date, schedule.end_time))

    existing_appointments = Appointment.objects.filter(
        master=master,
        start_at__date=date,
        status="CONFIRMED",
    )
    busy_intervals = [(a.start_at, a.end_at) for a in existing_appointments]

    duration = timedelta(minutes=duration_minutes)
    step = timedelta(minutes=step_minutes)

    available_slots = []
    current_start = work_start

    while current_start + duration <= work_end:
        current_end = current_start + duration

        has_conflict = False
        for busy_start, busy_end in busy_intervals:
            if current_start < busy_end and current_end > busy_start:
                has_conflict = True
                break

        if not has_conflict:
            available_slots.append((current_start, current_end))

        current_start += step

    return available_slots


def is_slot_still_available(master, start_at, end_at):
    slots = get_available_slots(master, start_at.date(), int((end_at - start_at).total_seconds() // 60))
    return any(s == start_at for s, e in slots)


@transaction.atomic
def create_appointment(client, master, service_list, start_at):
    total_duration = sum(s.duration_minutes for s in service_list)
    end_at = start_at + timedelta(minutes=total_duration)

    if not is_slot_still_available(master, start_at, end_at):
        raise ValidationError("This time is no longer available")

    appointment = Appointment.objects.create(client=client, master=master, start_at=start_at, end_at=end_at)
    for service in service_list:
        AppointmentService.objects.create(
            appointment=appointment, service=service, price_at_booking=service.base_price
        )
    return appointment
