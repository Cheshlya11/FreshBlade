from django.contrib.auth.forms import UserCreationForm

from .models import User


class ClientRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
