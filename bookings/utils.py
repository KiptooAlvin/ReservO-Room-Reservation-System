# bookings/utils.py
from django.db.models import Q
from .models import Booking

def bookings_conflict(room, new_check_in, new_check_out, exclude_booking_id=None):
    """
    Returns True if there is a conflicting booking for `room` in the interval.
    Overlap condition (standard):
        new_check_in < existing_check_out AND new_check_out > existing_check_in
    Only Approved and Pending bookings should block (adjust if needed).
    """
    qs = Booking.objects.filter(room=room).exclude(status=Booking.STATUS_DECLINED)
    if exclude_booking_id:
        qs = qs.exclude(pk=exclude_booking_id)
    conflict_q = qs.filter(
        Q(check_in__lt=new_check_out) & Q(check_out__gt=new_check_in)
    )
    return conflict_q.exists()
