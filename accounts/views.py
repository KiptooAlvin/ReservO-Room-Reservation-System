from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import UserRegistrationForm
from bookings.models import Booking

User= get_user_model()
def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data["password"]
            user.set_password(password)
            user.save()

            messages.success(request, "Account created successfully. You can now log in.")
            return redirect("accounts:login")

    else:
        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password","")

        user = authenticate(request,username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Welcome back!")
            return redirect("accounts:profile")
        else:
            if username and User.objects.filter(username=username).exists():
                messages.error(request, "Incorrect password.")
            else:
                messages.error(request, "Username does not exist.")
            return render(request, "accounts/login.html",{'username': username})

    return render(request, "accounts/login.html")


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("accounts:login")


@login_required
def profile_view(request):
    my_bookings = Booking.objects.filter(user=request.user).select_related("room")
    return render(request, "accounts/profile.html", {"bookings": my_bookings})
