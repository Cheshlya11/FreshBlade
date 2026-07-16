from django.contrib.auth.forms import UserCreationForm
from django import forms

from .models import User


class ClientRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        if commit:
            user.save()
        return user


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if User.objects.exclude(pk=self.instance.pk).filter(phone=phone).exists():
            raise forms.ValidationError("This phone number is already in use.")
        return phone
