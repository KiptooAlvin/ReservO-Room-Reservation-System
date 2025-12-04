from django import forms
from .models import Booking
from rooms.models import Room

class SearchAvailabilityForm(forms.Form):
    check_in = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    check_out = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    room_type = forms.ModelChoiceField(queryset=Room.objects.values_list('room_type', flat=True), required=False)

    # Note: For room_type we might want to use RoomType; adjust if necessary.

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
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    # Ensure room dropdown returns Room objects, NOT tuples
    room = forms.ModelChoiceField(
        queryset=Room.objects.all(),
        empty_label="Select a room",
    )

    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get('check_in')
        check_out = cleaned.get('check_out')
        if check_in and check_out and check_in >= check_out:
            raise forms.ValidationError("Check-out must be after check-in.")
        return cleaned
