# bookings/models.py
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

# Use string for room foreign key to avoid import-time circular issues
class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("checked_in", "Checked-in"),
        ("checked_out", "Checked-out"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    room = models.ForeignKey("rooms.Room", on_delete=models.CASCADE, related_name="bookings")
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveSmallIntegerField(default=1)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Booking #{self.pk or 'new'} - {self.room} by {self.user}"

    def clean(self):
        """
        Validation logic:
         - check_in < check_out
         - guests <= room.capacity
         - room must be available (no overlapping bookings, not under maintenance)
        """
        errors = {}

        if self.check_in >= self.check_out:
            errors["check_in"] = "Check-in date must be before check-out date."

        # Prevent booking in the past if desired (optional)
        # if self.check_in < timezone.now().date():
        #     errors["check_in"] = "Check-in date cannot be in the past."

        # Validate room and guest capacity
        if not self.room:
            errors["room"] = "A room must be selected."
        else:
            if self.guests and self.guests > self.room.capacity:
                errors["guests"] = f"Number of guests ({self.guests}) exceeds room capacity ({self.room.capacity})."

            # Check room status (maintenance/out_of_service)
            if self.room.status in ("maintenance", "out_of_service"):
                errors["room"] = "Selected room is currently unavailable (maintenance or out of service)."

            # Availability overlap check
            from bookings.models import Booking as BookingModel  # local name
            qs = BookingModel.objects.filter(room=self.room).exclude(status="cancelled")
            if self.pk:
                qs = qs.exclude(pk=self.pk)

            overlap_exists = qs.filter(check_in__lt=self.check_out, check_out__gt=self.check_in).exists()
            if overlap_exists:
                errors["room"] = "Selected room is already booked for the chosen dates."

        if errors:
            raise ValidationError(errors)

    def calculate_total_price(self):
        """
        Calculate total_price based on nights * room.price
        Nights is integer days between check_in and check_out.
        """
        nights = (self.check_out - self.check_in).days
        if nights <= 0:
            return Decimal("0.00")
        return Decimal(nights) * self.room.price

    def save(self, *args, **kwargs):
        # Run full clean to enforce validations (this raises ValidationError if invalid)
        self.full_clean()

        # Compute price automatically
        if self.check_in and self.check_out and self.room:
            self.total_price = self.calculate_total_price()

        super().save(*args, **kwargs)
