from django.db import models
from bookings.models import Booking
from rooms.models import Room
from django.contrib.auth.models import User

class DashboardData(models.Model):
    """
    Optional model for storing any precomputed stats if needed
    """
    created_at = models.DateTimeField(auto_now_add=True)
