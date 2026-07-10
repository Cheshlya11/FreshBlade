from django.contrib import admin
from .models import Appointment, AppointmentService, MasterSchedule


class AppointmentServiceInline(admin.TabularInline):
    model = AppointmentService
    extra = 1


class AppointmentAdmin(admin.ModelAdmin):
    inlines = [AppointmentServiceInline]

admin.site.register(MasterSchedule)
admin.site.register(Appointment, AppointmentAdmin)
