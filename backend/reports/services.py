from django.db.models import Count, Sum, Q, Value, DecimalField
from django.db.models.functions import Coalesce

from accounts.models import Master, User
from catalog.models import Service
from booking.models import Appointment, AppointmentService


def get_master_performance_report(date_from=None, date_to=None):
    columns = [
        "Master",
        "Email",
        "Phone",
        "Confirmed",
        "Cancelled",
        "Completed",
        "Revenue",
    ]
    rows = []

    appointment_filter = Q()
    if date_from:
        appointment_filter &= Q(appointments__start_at__date__gte=date_from)
    if date_to:
        appointment_filter &= Q(appointments__start_at__date__lte=date_to)

    masters = Master.objects.annotate(
        confirmed_count=Count(
            "appointments",
            filter=Q(appointments__status=Appointment.Status.CONFIRMED)
            & appointment_filter,
        ),
        cancelled_count=Count(
            "appointments",
            filter=Q(appointments__status=Appointment.Status.CANCELLED)
            & appointment_filter,
        ),
        completed_count=Count(
            "appointments",
            filter=Q(appointments__status=Appointment.Status.COMPLETED)
            & appointment_filter,
        ),
        total_revenue=Coalesce(
            Sum(
                "appointments__appointmentservice__price_at_booking",
                filter=Q(appointments__status=Appointment.Status.COMPLETED)
                & appointment_filter,
            ),
            Value(0),
            output_field=DecimalField(),
        ),
    ).order_by("-total_revenue")

    for master in masters:
        rows.append(
            [
                master.user.get_full_name(),
                master.user.email,
                master.user.phone,
                master.confirmed_count,
                master.cancelled_count,
                master.completed_count,
                f"{master.total_revenue or 0}€",
            ]
        )

    return columns, rows


def get_service_revenue_report(date_from=None, date_to=None):
    columns = ["Service", "Base price", "Times booked", "Cancelled", "Revenue"]
    rows = []

    appointment_filter = Q()
    if date_from:
        appointment_filter &= Q(appointments__start_at__date__gte=date_from)
    if date_to:
        appointment_filter &= Q(appointments__start_at__date__lte=date_to)

    services = Service.objects.annotate(
        booking_count=Count(
            "appointmentservice",
            filter=Q(
                appointmentservice__appointment__status=Appointment.Status.COMPLETED
            )
            & appointment_filter,
        ),
        cancelled_count=Count(
            "appointmentservice",
            filter=Q(
                appointmentservice__appointment__status=Appointment.Status.CANCELLED
            )
            & appointment_filter,
        ),
        total_revenue=Coalesce(
            Sum(
                "appointmentservice__price_at_booking",
                filter=Q(
                    appointmentservice__appointment__status=Appointment.Status.COMPLETED
                )
                & appointment_filter,
            ),
            Value(0),
            output_field=DecimalField(),
        ),
    ).order_by("-total_revenue")

    for service in services:
        rows.append(
            [
                service.name,
                f"{service.base_price}€",
                service.booking_count,
                service.cancelled_count,
                f"{service.total_revenue or 0}€",
            ]
        )

    return columns, rows


def get_client_activity_report(date_from=None, date_to=None):
    columns = ["Client", "Email", "Phone", "Visits", "Total spent"]
    rows = []

    appointment_filter = Q()
    if date_from:
        appointment_filter &= Q(client_appointments__start_at__date__gte=date_from)
    if date_to:
        appointment_filter &= Q(client_appointments__start_at__date__lte=date_to)

    clients = (
        User.objects.filter(role="CLIENT")
        .annotate(
            visit_count=Count(
                "client_appointments",
                filter=Q(client_appointments__status=Appointment.Status.COMPLETED)
                & appointment_filter,
            ),
            total_spent=Coalesce(
                Sum(
                    "client_appointments__appointmentservice__price_at_booking",
                    filter=Q(client_appointments__status=Appointment.Status.COMPLETED)
                    & appointment_filter,
                ),
                Value(0),
                output_field=DecimalField(),
            ),
        )
        .order_by("-visit_count")
    )
    for client in clients:
        rows.append(
            [
                client.get_full_name(),
                client.email,
                client.phone,
                client.visit_count,
                f"{client.total_spent or 0}€",
            ]
        )

    return columns, rows


def get_status_summary_report(date_from=None, date_to=None):
    columns = ["Status", "Count", "Revenue", "Percentage"]
    rows = []

    date_filter_appointment = Q()
    if date_from:
        date_filter_appointment &= Q(start_at__date__gte=date_from)
    if date_to:
        date_filter_appointment &= Q(start_at__date__lte=date_to)

    date_filter_service = Q()
    if date_from:
        date_filter_service &= Q(appointment__start_at__date__gte=date_from)
    if date_to:
        date_filter_service &= Q(appointment__start_at__date__lte=date_to)

    total_count = Appointment.objects.filter(date_filter_appointment).count()
    total_revenue = 0

    for status_value, status_label in Appointment.Status.choices:
        count = Appointment.objects.filter(
            Q(status=status_value) & date_filter_appointment
        ).count()

        percentage = (count / total_count * 100) if total_count > 0 else 0

        revenue = (
            AppointmentService.objects.filter(
                Q(appointment__status=status_value) & date_filter_service
            ).aggregate(total=Sum("price_at_booking"))["total"]
            or 0
        )

        if status_value == Appointment.Status.CONFIRMED:
            revenue_display = f"+{revenue}€ (expected)"
            total_revenue += revenue
        elif status_value == Appointment.Status.CANCELLED:
            revenue_display = f"-{revenue}€ (lost)"
        else:
            revenue_display = f"{revenue}€"
            total_revenue += revenue

        rows.append([status_label, count, revenue_display, f"{percentage:.1f}%"])

    rows.append(["Total", total_count, f"{total_revenue}€", "100.0%"])

    return columns, rows
