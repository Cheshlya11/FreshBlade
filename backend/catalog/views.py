from django.shortcuts import render
from .models import Service


def service_list_view(request):
    services = Service.objects.filter(is_active=True).order_by("name")
    return render(request, "catalog/services.html", {"services": services})
