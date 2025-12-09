from django import forms
from .models import Booking
from rooms.models import Room
from datetime import date



# ---------------------------------------------------------
# SEARCH AVAILABILITY FORM
# ---------------------------------------------------------
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

    # Room type will be injected dynamically in __init__
    room_type = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select(attrs={
            "class": "form-control form-control-lg shadow-sm rounded-3",
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fetch DISTINCT room types dynamically from Room model
        room_types = Room.objects.values_list("room_type", flat=True).distinct()

        # Build dropdown choices
        choices = [("", "Any Room Type")] + [(rt, rt.title()) for rt in room_types]

        self.fields["room_type"].choices = choices


# ---------------------------------------------------------
# BOOKING FORM
# ---------------------------------------------------------
class BookingForm(forms.ModelForm):

    # Apply styling to room dropdown
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
            'total_price',
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
            'total_price': forms.NumberInput(attrs={'readonly': 'readonly', 'id': 'total_price_field',
            "class": "form-control form-control-lg shadow-sm rounded-3",
                                                    }),
        }

    # Date validation

    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get('check_in')
        check_out = cleaned.get('check_out')

        # Check that dates exist
        if not check_in or not check_out:
            return cleaned

        # 1️⃣ Prevent booking in the past
        today = date.today()
        if check_in < today:
            raise forms.ValidationError("Check-in date cannot be in the past.")

        # 2️⃣ Prevent checkout being before/at check-in
        if check_in >= check_out:
            raise forms.ValidationError("Check-out must be after check-in.")

        return cleaned

