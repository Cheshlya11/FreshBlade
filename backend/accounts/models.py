from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = "CLIENT", "Client"
        MASTER = "MASTER", "Master"

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CLIENT)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "phone"]


class Master(models.Model):
    user = models.OneToOneField(
        User, primary_key=True, on_delete=models.CASCADE, related_name="master_profile"
    )
    bio = models.TextField(blank=True)
    short_description = models.CharField(max_length=255, blank=True)
    expirience_years = models.PositiveIntegerField(default=0)
    photo = models.ImageField(upload_to="masters/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name()
