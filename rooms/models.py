from django.db import models
from decimal import  Decimal
# Create your models here.
class Room(models.Model):
    ROOM_TYPES =[
        ("single","Single"),
        ("double","Double"),
        ("suite","Suite"),
        ("conference","Conference")
    ]
    STATUS_CHOICES=[
        ("available","Available"),
        ("booked","Booked"),
        ("maintenance","Maintenance"),
        ("out_of_service","Out of Service")
    ]

    room_number= models.CharField(max_length=20, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default="single")
    price=models.DecimalField(decimal_places=2, max_digits=10)
    capacity=models.PositiveSmallIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    description = models.TextField(blank=True)
    image=models.ImageField(upload_to="rooms/", blank=True)

    class Meta:
        ordering=["room_number"]

    def __str__(self):
        return f"Room: {self.room_number} ({self.get_room_type_display()}) "

    def is_available_for_period(self, check_in, check_out,exclude_booking_id=None):
        """
                Convenience method that delegates to booking availability logic.
                It will return False if the room status makes it unavailable (maintenance/out_of_service)
                or if an overlapping booking exists.
                """
        if self.status in ("maintenance", "out_of_service"):
            return  False
        # Important to have circular import at module load time
        from bookings.models import   Booking
        qs = Booking.objects.filter(room=self).exclude(status="cancelled")
        if exclude_booking_id:
            qs = qs.exclude(pk=exclude_booking_id)

#         overlap rule: new_checkin < existing_checkout AND new_checkout > existing_checkin
        overlaps= qs.filter(check_in_ly= check_out,check_out_gt=check_in).exists()
        return not overlaps

