from django import forms
from django.db.models import Case, When, Value, IntegerField

from catalog.models import Service
from accounts.models import Master


class ServiceCheckboxSelect(forms.CheckboxSelectMultiple):
    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
        if value:
            service_id = value.value if hasattr(value, "value") else value
            service = Service.objects.get(pk=service_id)
            option["attrs"]["data-duration"] = service.duration_minutes
            option["attrs"]["data-price"] = str(service.base_price)
            option["attrs"]["title"] = service.description
        return option


class AppointmentForm(forms.Form):
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.filter(is_active=True)
        .annotate(
            sort_order=Case(
                When(category="haircut", then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        )
        .order_by("sort_order", "name"),
        widget=ServiceCheckboxSelect,
    )
    master = forms.ModelChoiceField(
        queryset=Master.objects.filter(is_active=True),
        empty_label="Select a master",
    )
    start_at = forms.DateTimeField()

    def clean_services(self):
        services = self.cleaned_data["services"]
        if len(services) > 3:
            raise forms.ValidationError("You can select up to 3 services per visit.")

        haircut_services = [s for s in services if s.category == "haircut"]
        if len(haircut_services) > 1:
            raise forms.ValidationError(
                "You can only select one type of haircut per visit."
            )

        return services


class AppointmentFilterForm(forms.Form):
    STATUS_CHOICES = [
        ("CONFIRMED", "Confirmed"),
        ("COMPLETED", "Past"),
        ("CANCELLED", "Cancelled"),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES, required=False, initial="CONFIRMED"
    )
    master = forms.ModelChoiceField(
        queryset=Master.objects.filter(is_active=True), required=False
    )
    search = forms.CharField(required=False)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user.role == "MASTER":
            del self.fields["master"]
        elif user.role == "CLIENT":
            del self.fields["search"]

        if user.is_staff:
            pass
