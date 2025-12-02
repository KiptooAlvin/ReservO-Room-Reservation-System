from django.db import models
from decimal import  Decimal
# Create your models here.
class Room(models.Model):
    ROOM_TYPES = [
        ("single", "Single"),
        ("double", "Double"),
        ("suite", "Suite"),
        ("conference", "Conference"),
    ]

    STATUS_CHOICES = [
        ("available", "Available"),
        ("booked", "Booked"),
        ("maintenance", "Maintenance"),
        ("out_of_service", "Out of Service"),
    ]

    room_number = models.CharField(max_length=20, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='single')
    price = models.DecimalField(decimal_places=2, max_digits=10)
    capacity = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="rooms/", blank=True)

    class Meta:
        ordering = ["room_number"]

    def __str__(self):
        return f"Room: {self.room_number} ({self.get_room_type_display()})"

    def is_available_for_period(self, check_in, check_out, exclude_booking_id=None):
        if self.status in ("maintenance", "out_of_service"):
            return False

        from bookings.models import Booking
        qs = Booking.objects.filter(room=self).exclude(status="cancelled")
        if exclude_booking_id:
            qs = qs.exclude(pk=exclude_booking_id)

        overlaps = qs.filter(
            check_in__lt=check_out,
            check_out__gt=check_in
        ).exists()

        return not overlaps

    def is_available(self, check_in, check_out):
        return not self.booking_set.filter(
            check_in__lt=check_out,
            check_out__gt=check_in
        ).exists()
