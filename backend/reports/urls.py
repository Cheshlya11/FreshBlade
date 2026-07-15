from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.report_view, name="report"),
    path("export/", views.report_export_view, name="report_export"),
]
