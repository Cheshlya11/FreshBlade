from django.urls import path
from . import views

app_name = "booking"

urlpatterns = [
    path("available-slots/", views.available_slots_view, name="available_slots"),
    path("new/", views.booking_create_view, name="create")
]
