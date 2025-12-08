from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control form-control-lg shadow-sm rounded-3",

        })
    )

    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control form-control-lg shadow-sm rounded-3",

        })
    )

    class Meta:
        model = User
        fields = ["username", "email"]

        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control form-control-lg shadow-sm rounded-3",

            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control form-control-lg shadow-sm rounded-3",

            }),
        }

        labels = {
            "username": "Username",
            "email": "Email Address",
        }

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password")
        p2 = cleaned.get("confirm_password")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError(" Passwords do not match. Please try again.")

        return cleaned
