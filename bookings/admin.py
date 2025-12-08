from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "room", "check_in", "check_out", "guests", "total_price", "status")
    list_filter = ("status", "check_in", "check_out")
    search_fields = ("user__username", "room__room_number")
    readonly_fields = ("total_price", "created_at")

    actions = ["mark_approved", "mark_declined"]

    @admin.action(description="Mark selected bookings as Approved")
    def mark_approved(self, request, queryset):
        updated = queryset.update(status=Booking.STATUS_APPROVED)
        self.message_user(request, f"{updated} booking(s) marked as Approved.")

    @admin.action(description="Mark selected bookings as Declined")
    def mark_declined(self, request, queryset):
        updated = queryset.update(status=Booking.STATUS_DECLINED)
        self.message_user(request, f"{updated} booking(s) marked as Declined.")
