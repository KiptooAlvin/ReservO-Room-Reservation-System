from django.contrib import admin

from rooms.models import Room
# Register your models here.

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number','room_type','price','capacity','status')
    list_filter = ('room_type','status')
    search_fields = ('room_number','description')
