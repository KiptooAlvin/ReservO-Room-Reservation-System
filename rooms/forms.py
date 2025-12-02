from django import forms
from .models import Room

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields= ['room_number','room_type','price','capacity','status','image']