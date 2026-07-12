from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    full_description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField()
    photo = models.URLField(blank=True)
    category = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
