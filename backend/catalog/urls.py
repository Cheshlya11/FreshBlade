from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("services/", views.service_list_view, name="service_list"),
    path("masters/", views.master_list_view, name="master_list"),
]
