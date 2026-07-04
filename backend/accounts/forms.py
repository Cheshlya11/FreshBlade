from django.contrib.auth.forms import UserCreationForm

from .models import User


class ClientRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone"]
