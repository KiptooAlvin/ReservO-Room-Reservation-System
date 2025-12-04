from django.contrib.auth.decorators import user_passes_test
from django.urls import path

from bookings.views import is_admin
from . import views

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('create/', user_passes_test(is_admin)(views.room_create), name='room_create'),
    path('update/<int:pk>/', views.room_update, name='room_update'),
    path('delete/<int:pk>/', views.room_delete, name='room_delete'),
]