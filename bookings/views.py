from django.shortcuts import render, redirect, get_object_or_404
from .models import Booking
from .forms import BookingForm
from django.contrib import messages

def booking_list(request):
    bookings = Booking.objects.all()
    return render(request, 'bookings/booking_list.html', {'bookings': bookings})

def booking_create(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)

            # Check availability
            if not booking.room.is_available_for_period(booking.check_in, booking.check_out):
                messages.error(request, "Room is NOT available for the selected dates.")
                return render(request, 'bookings/booking_form.html', {'form': form})

            booking.total_price = booking.calculate_total_price()
            booking.save()
            return redirect('booking_list')
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

            # # Only re-check if room or dates changed
            # if (new_booking.room != old_room or new_booking.check_in != old_in or new_booking.check_out != old_out):
            #     if not new_booking.room.is_available(new_booking.check_in, new_booking.check_out):
            #         messages.error(request, "Room is not available for the updated dates.")
            #         return render(request, 'bookings/booking_form.html', {'form': form})

            new_booking.total_price = new_booking.calculate_total_price()
            new_booking.save()
            return redirect('booking_list')

    else:
        form = BookingForm(instance=booking)

    return render(request, 'bookings/booking_form.html', {'form': form})


def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.method == 'POST':
        booking.delete()
        return redirect('booking_list')

    return render(request, 'bookings/booking_delete.html', {'booking': booking})
