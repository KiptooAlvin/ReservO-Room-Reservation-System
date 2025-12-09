from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from .models import Booking
from .forms import SearchAvailabilityForm, BookingForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction

from .utils import bookings_conflict
from rooms.models import Room


# -----------------------------
# SEARCH AVAILABILITY
# -----------------------------
# from django.db.models import Q

def search_availability(request):
    """
    Page where users enter check-in/out and get a list of available rooms.
    Now respects room_type (and guests if present) and excludes rooms with overlapping bookings.
    """
    form = SearchAvailabilityForm(request.GET or None)
    available_rooms = None

    if form.is_valid():
        check_in = form.cleaned_data['check_in']
        check_out = form.cleaned_data['check_out']

        if check_in >= check_out:
            messages.error(request, "Check-out must be after check-in.")
        else:
            # start with all rooms
            rooms_qs = Room.objects.all()

            # apply room_type filter if the form provides it
            room_type = form.cleaned_data.get('room_type')
            if room_type:
                rooms_qs = rooms_qs.filter(room_type=room_type)

            # apply guests/capacity filter if your form has it
            guests = form.cleaned_data.get('guests')
            if guests:
                # assumes Room has a 'capacity' integer field
                rooms_qs = rooms_qs.filter(capacity__gte=guests)

            # Exclude rooms that have bookings overlapping the requested period.
            # Overlap condition: booking.check_in < check_out AND booking.check_out > check_in
            conflicting_bookings = Booking.objects.filter(
                room__in=rooms_qs,
                check_in__lt=check_out,
                check_out__gt=check_in
            ).values_list('room_id', flat=True).distinct()

            rooms_qs = rooms_qs.exclude(id__in=conflicting_bookings)

            # At this point rooms_qs contains only rooms matching filters and WITHOUT overlapping bookings.
            # If you still want per-room custom checks (e.g. considering only APPROVED bookings),
            # you can either change the Booking filter above to .filter(status=...) or fallback to bookings_conflict loop.

            available_rooms = list(rooms_qs)

    context = {
        'form': form,
        'available_rooms': available_rooms,
    }
    return render(request, 'bookings/search_availability.html', context)


# -----------------------------
# BOOKING LIST
# -----------------------------
@login_required
def booking_list(request):
    """
    Admin sees all bookings.
    Users see only their own.
    """
    if request.user.is_staff:
        bookings = Booking.objects.all()
    else:
        bookings = Booking.objects.filter(user=request.user)

    return render(request, 'bookings/booking_list.html', {
        'bookings': bookings
    })


# -----------------------------
# BOOKING CREATE
# -----------------------------
@login_required
@transaction.atomic
def booking_create(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)

        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user

            # check conflicts
            if bookings_conflict(booking.room, booking.check_in, booking.check_out):
                messages.error(request, "Room is NOT available for the selected dates.")
                return render(request, 'bookings/booking_form.html', {'form': form})

            booking.total_price = booking.calculate_total_price()
            booking.save()
            messages.success(request, "Booking created successfully.")
            return redirect('bookings:booking_list')

    else:
        form = BookingForm()

    return render(request, 'bookings/booking_form.html', {'form': form})


# -----------------------------
# BOOKING UPDATE (Admin or Internal Use)
# -----------------------------
@login_required
def booking_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    old_room = booking.room
    old_in = booking.check_in
    old_out = booking.check_out

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)

        if form.is_valid():
            new_booking = form.save(commit=False)

            # re-check only if something changed
            if (new_booking.room != old_room or
                    new_booking.check_in != old_in or
                    new_booking.check_out != old_out):

                if bookings_conflict(new_booking.room, new_booking.check_in, new_booking.check_out, exclude_booking_id=pk):
                    messages.error(request, "Room is not available for updated dates.")
                    return render(request, 'bookings/booking_form.html', {'form': form})

            new_booking.total_price = new_booking.calculate_total_price()
            new_booking.save()
            messages.success(request, "Booking updated successfully.")
            return redirect('accounts:profile')

    else:
        form = BookingForm(instance=booking)

    return render(request, 'bookings/booking_form.html', {'form': form})


# -----------------------------
# BOOKING DELETE
# -----------------------------
@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

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


# -----------------------------
# ADMIN FUNCTIONS
# -----------------------------
def is_admin(user):
    return user.is_staff or user.is_superuser


@user_passes_test(is_admin)
def pending_bookings_list(request):
    bookings = Booking.objects.filter(status=Booking.STATUS_PENDING).select_related('room', 'user')
    return render(request, 'bookings/pending_list.html', {'bookings': bookings})


@staff_member_required
def approve_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    booking.status = Booking.STATUS_APPROVED
    booking.save()

    messages.success(request, f"Booking #{booking.id} approved successfully.")
    return redirect('bookings:booking_list')


@staff_member_required
def decline_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    booking.status = Booking.STATUS_DECLINED
    booking.save()

    messages.success(request, f"Booking #{booking.id} declined.")
    return redirect('bookings:booking_list')


# -----------------------------
# BOOKING EDIT (User Only)
# -----------------------------
@login_required
def booking_edit(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if booking.user != request.user:
        return HttpResponseForbidden("You cannot edit someone else’s booking.")

    if booking.status != Booking.STATUS_PENDING:
        messages.error(request, "Only pending bookings can be edited.")
        return redirect("accounts:profile")

    if request.method == "POST":
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            edited = form.save(commit=False)

            if bookings_conflict(
                    edited.room, edited.check_in, edited.check_out, exclude_booking_id=booking.pk):
                messages.error(request, "Room is not available for those dates.")
                return redirect("accounts:profile")

            edited.total_price = edited.calculate_total_price()
            edited.save()
            messages.success(request, "Booking updated successfully.")
            return redirect("accounts:profile")
    else:
        form = BookingForm(instance=booking)

    return render(request, "bookings/booking_form.html", {"form": form, "booking": booking})


# -----------------------------
# USER BOOKINGS PAGE
# -----------------------------
@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-check_in')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})
