from django import forms
from .models import Booking
from rooms.models import Room

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "user",
            "room",
            "check_in",
            "check_out",
            "guests",
            "notes",
        ]
        widgets = {
            "check_in": forms.DateInput(attrs={"type": "date"}),
            "check_out": forms.DateInput(attrs={"type": "date"}),
        }

    # Ensure room dropdown returns Room objects, NOT tuples
    room = forms.ModelChoiceField(
        queryset=Room.objects.all(),
        empty_label="Select a room",
    )
