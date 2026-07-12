from django.shortcuts import render
from django.db.models import Count
from .models import Service
from accounts.models import Master


def service_list_view(request):
    services = Service.objects.filter(is_active=True).order_by("name")
    return render(request, "catalog/services.html", {"services": services})


def master_list_view(request):
    masters = (
        Master.objects.filter(is_active=True)
        .annotate(appointment_count=Count("appointments"))
        .order_by("-appointment_count")
    )
    return render(request, "catalog/masters.html", {"masters": masters})
