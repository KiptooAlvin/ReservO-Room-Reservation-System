from django.shortcuts import render
from bookings.models import Booking
from rooms.models import Room
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST

def admin_dashboard(request):
    total_rooms = Room.objects.count()
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status=Booking.STATUS_PENDING).count()
    approved_today = Booking.objects.filter(status=Booking.STATUS_APPROVED, check_in=now().date()).count()
    total_users = User.objects.count()

    recent_bookings = Booking.objects.order_by('-check_in')[:10]
    room_types = Room.objects.values('room_type').annotate(count=Count('id'))
    monthly_bookings = (
        Booking.objects.extra(select={'month': "strftime('%%m', check_in)"}).values('month')
        .annotate(count=Count('id')).order_by('month')
    )

    pending_queue = Booking.objects.filter(status=Booking.STATUS_PENDING).order_by('check_in')

    context = {
        'total_rooms': total_rooms,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'approved_today': approved_today,
        'total_users': total_users,
        'recent_bookings': recent_bookings,
        'room_types': list(room_types),
        'monthly_bookings': list(monthly_bookings),
        'pending_queue': pending_queue,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

@require_POST
def approve_decline_booking(request):
    booking_id = request.POST.get('booking_id')
    action = request.POST.get('action')
    if not booking_id or not action:
        return JsonResponse({'success': False, 'error': 'Missing data'})

    try:
        booking = Booking.objects.get(id=booking_id)
        if action.lower() == 'approve':
            booking.status = Booking.STATUS_APPROVED
        elif action.lower() == 'decline':
            booking.status = Booking.STATUS_DECLINED
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'})
        booking.save()
        return JsonResponse({'success': True, 'status': booking.status})
    except Booking.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Booking not found'})
