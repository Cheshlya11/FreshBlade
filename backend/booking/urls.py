from django.urls import path
from . import views

app_name = "booking"

urlpatterns = [
    path("available-slots/", views.available_slots_view, name="available_slots"),
    path("new/", views.booking_create_view, name="create"),
    path("my-appointments/", views.my_appointments_view, name="my_appointments"),
    path("cancel/<int:appointment_id>/", views.cancel_appointment_view, name="cancel"),
    path(
        "complete/<int:appointment_id>/",
        views.complete_appointment_view,
        name="complete",
    ),
    path("complete-all/", views.complete_all_appointments_view, name="complete_all"),
]
