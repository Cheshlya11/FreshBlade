from django.db import models

from accounts.models import User, Master
from catalog.models import Service


class MasterSchedule(models.Model):
    class Weekday(models.IntegerChoices):
        MON = (
            1,
            "Monday",
        )
        TUE = (
            2,
            "Tuesday",
        )
        WED = (
            3,
            "Wednesday",
        )
        THU = (
            4,
            "Thursday",
        )
        FRI = (
            5,
            "Friday",
        )
        SAT = (
            6,
            "Saturday",
        )
        SUN = 7, "Sunday"

    master = models.ForeignKey(
        Master, on_delete=models.CASCADE, related_name="schedules"
    )
    weekday = models.PositiveSmallIntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["master", "weekday"], name="uq_master_weekday"
            ),
            models.CheckConstraint(
                condition=models.Q(start_time__lt=models.F("end_time")),
                name="chk_schedule_time",
            ),
        ]


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        CANCELLED = "CANCELLED", "Cancelled"
        COMPLETED = "COMPLETED", "Completed"

    client = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="client_appointments"
    )
    master = models.ForeignKey(
        Master, on_delete=models.CASCADE, related_name="appointments"
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="appointments"
    )

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_at__gt=models.F("start_at")),
                name="chk_appointments_time",
            ),
        ]
