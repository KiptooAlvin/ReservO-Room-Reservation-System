from django.urls import path
from . import views

app_name = "bookings"
urlpatterns = [
    path('', views.my_bookings, name='my_bookings'),
    path('', views.booking_list, name='booking_list'),

    path('create/', views.booking_create, name='booking_create'),
    path('update/<int:pk>', views.booking_update, name='booking_update'),
    path('delete/<int:pk>', views.booking_delete, name='booking_delete'),
path("edit/<int:pk>/", views.booking_edit, name="edit"),
    path('search/', views.search_availability, name='search-availability'),





]