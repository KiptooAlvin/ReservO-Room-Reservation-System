from django import forms
from .models import Booking
from rooms.models import Room
from django import forms
from .models import Booking
from rooms.models import Room


class SearchAvailabilityForm(forms.Form):
    check_in = forms.DateField(
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control form-control-lg shadow-sm rounded-3",
        })
    )
    check_out = forms.DateField(
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control form-control-lg shadow-sm rounded-3",
        })
    )

    # Fixed: RoomType must be a ChoiceField, not a ModelChoiceField with values_list
    room_type = forms.ChoiceField(
        required=False,
        choices=[("", "Any Room Type")] ,
                # + [(rt, rt) for rt in Room.objects.values_list("room_type", flat=True).distinct()],
        widget=forms.Select(attrs={
            "class": "form-control form-control-lg shadow-sm rounded-3"
        })
    )


class BookingForm(forms.ModelForm):

    # override room dropdown with styling
    room = forms.ModelChoiceField(
        queryset=Room.objects.all(),
        empty_label="Select a Room",
        widget=forms.Select(attrs={
            "class": "form-control form-control-lg shadow-sm rounded-3",
        })
    )

    class Meta:
        model = Booking
        fields = [
            "room",
            "check_in",
            "check_out",
            "guests",
            "notes",
        ]

        widgets = {
            "check_in": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control form-control-lg shadow-sm rounded-3",
            }),
            "check_out": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control form-control-lg shadow-sm rounded-3",
            }),
            "guests": forms.NumberInput(attrs={
                "class": "form-control form-control-lg shadow-sm rounded-3",
                "placeholder": "Number of guests",
                "min": "1"
            }),
            "notes": forms.Textarea(attrs={
                "rows": 3,
                "class": "form-control form-control-lg shadow-sm rounded-3",
                "placeholder": "Optional notes..."
            }),
        }

    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get('check_in')
        check_out = cleaned.get('check_out')

        if check_in and check_out and check_in >= check_out:
            raise forms.ValidationError("Check-out must be after check-in.")

        return cleaned
