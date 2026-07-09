from datetime import datetime

from django.http import JsonResponse
from django.utils import timezone

from accounts.models import Master
from .services import get_available_slots


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
