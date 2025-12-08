from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from .models import Booking
from .forms import  SearchAvailabilityForm, BookingForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction


from .utils import bookings_conflict
from rooms.models import Room

def search_availability(request):
    """
    Page where users enter check-in/out and get a list of available rooms.
    """
    form = SearchAvailabilityForm(request.GET or None)
    available_rooms = None
    if form.is_valid():
        check_in = form.cleaned_data['check_in']
        check_out = form.cleaned_data['check_out']
        # Basic validation
        if check_in >= check_out:
            messages.error(request, "Check-out must be after check-in.")
        else:
            # Start with all rooms (optionally filter by type/capacity)
            rooms_qs = Room.objects.all()
            # Optionally filter by room_type if your form captures it correctly
            # If you captured RoomType properly:
            # room_type = form.cleaned_data.get('room_type')
            # if room_type:
            #     rooms_qs = rooms_qs.filter(room_type=room_type)

            # Exclude rooms that have conflicting bookings
            available = []
            for room in rooms_qs:
                if not bookings_conflict(room, check_in, check_out):
                    available.append(room)
            available_rooms = available

    context = {
        'form': form,
        'available_rooms': available_rooms,
    }
    return render(request, 'bookings/search_availability.html', context)
@login_required
def booking_list(request):
    bookings = Booking.objects.all()
    return render(request, 'bookings/booking_list.html', {'bookings': bookings})

@login_required
@transaction.atomic
def booking_create(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)

            booking.user = request.user

            # Check availability
            if not booking.room.is_available_for_period(booking.check_in, booking.check_out):
                messages.error(request, "Room is NOT available for the selected dates.")
                return render(request, 'bookings/booking_list.html', {'form': form})

            booking.total_price = booking.calculate_total_price()
            booking.save()
            return redirect('bookings:booking_list')
    else:
        form = BookingForm()

    return render(request, 'bookings/booking_form.html', {'form': form})


def booking_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    old_room = booking.room
    old_in = booking.check_in
    old_out = booking.check_out

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)

        if form.is_valid():
            new_booking = form.save(commit=False)

            # Only re-check if room or dates changed
            if new_booking.room != old_room or new_booking.check_in != old_in or new_booking.check_out != old_out:
                if not new_booking.room.is_available(new_booking.check_in, new_booking.check_out):
                    messages.error(request, "Room is not available for the updated dates.")
                    return render(request, 'bookings/booking_form.html', {'form': form})

            new_booking.total_price = new_booking.calculate_total_price()
            new_booking.save()
            return redirect('accounts:profile')

    else:
        form = BookingForm(instance=booking)

    return render(request, 'bookings/booking_form.html', {'form': form})


@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    # SECURITY CHECKS
    if booking.user != request.user:
        return HttpResponseForbidden("You cannot delete someone else’s booking.")

    if booking.status != Booking.STATUS_PENDING:
        messages.error(request, "Only pending bookings can be deleted.")
        return redirect("accounts:profile")

    if request.method == "POST":
        booking.delete()
        messages.success(request, "Booking deleted successfully.")
        return redirect("accounts:profile")

    return render(request, "bookings/booking_delete.html", {"booking": booking})
# Admin-only views (simple checks; use django admin or staff_required as needed)
def is_admin(user):
    return user.is_staff or user.is_superuser

@user_passes_test(is_admin)
def pending_bookings_list(request):
    bookings = Booking.objects.filter(status=Booking.STATUS_PENDING).select_related('room', 'user')
    return render(request, 'bookings/pending_list.html', {'bookings': bookings})


@staff_member_required
def approve_booking(request, pk):
    booking = Booking.objects.get(pk=pk)
    booking.status = Booking.STATUS_APPROVED
    booking.save()
    """
    # Optional email notification
    send_mail(
        subject='Booking Approved',
        message=f"Your booking for {booking.room} from {booking.check_in} to {booking.check_out} has been approved.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[booking.user.email],
    )
    """
    messages.success(request, f"Booking  # {booking.id}approved successfully.")
    return redirect('bookings:booking_list')

@staff_member_required
def decline_booking(request, pk):
    booking = Booking.objects.get(pk=pk)
    booking.status = Booking.STATUS_DECLINED
    booking.save()

    """
     # Optional email notification
    send_mail(
        subject='Booking Declined',
        message=f"Your booking for {booking.room} from {booking.check_in} to {booking.check_out} has been declined.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[booking.user.email],
    )
    """
    messages.success(request, f"Booking {booking.id} declined.")
    return redirect('bookings:booking_list')

@login_required
def booking_edit(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    # SECURITY: user can edit ONLY their own pending booking
    if booking.user != request.user:
        return HttpResponseForbidden("You cannot edit someone else’s booking.")

    if booking.status != Booking.STATUS_PENDING:
        messages.error(request, "Only pending bookings can be edited.")
        return redirect("accounts:profile")

    if request.method == "POST":
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            edited = form.save(commit=False)

            # conflict check
            if bookings_conflict(edited.room, edited.check_in, edited.check_out, exclude_booking_id=booking.pk):
                messages.error(request, "That room is not available for the chosen dates.")
                return redirect("accounts:profile")

            edited.save()
            messages.success(request, "Booking updated successfully.")
            return redirect("accounts:profile")
    else:
        form = BookingForm(instance=booking)

    return render(request, "bookings/booking_form.html", {"form": form, "booking": booking})
@login_required
def my_bookings(request):
    """
    Dedicated page showing bookings for the logged-in user only.
    """
    bookings = Booking.objects.filter(user=request.user).order_by('-check_in')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})
