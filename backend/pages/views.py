from django.shortcuts import render
from django.db.models import Count, Q

from catalog.models import Service
from accounts.models import Master


def home_view(request):
    top_services = Service.objects.filter(is_active=True).annotate(
        booking_count=Count("appointmentservice", filter=Q(appointmentservice__appointment__status="COMPLETED"))
    ).order_by("-booking_count", "name")[:3]

    top_masters = Master.objects.filter(is_active=True).order_by("-experience_years")[:3]

    return render(request, "pages/home.html", {"top_services": top_services, "top_masters": top_masters})
