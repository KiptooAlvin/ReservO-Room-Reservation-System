from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('booking-action/', views.approve_decline_booking, name='booking_action'),
]
