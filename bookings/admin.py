# bookings/admin.py
from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "room", "check_in", "check_out", "guests", "total_price", "status")
    list_filter = ("status", "check_in", "check_out")
    search_fields = ("user__username", "room__room_number")
    readonly_fields = ("total_price", "created_at")
    actions = ["mark_confirmed", "mark_cancelled"]

    def mark_confirmed(self, request, queryset):
        updated = queryset.update(status="confirmed")
        self.message_user(request, f"{updated} booking(s) marked confirmed.")
    mark_confirmed.short_description = "Mark selected bookings as Confirmed"

    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status="cancelled")
        self.message_user(request, f"{updated} booking(s) marked cancelled.")
    mark_cancelled.short_description = "Mark selected bookings as Cancelled"
