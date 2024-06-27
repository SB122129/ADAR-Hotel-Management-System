# urls.py

from django.urls import path
from .views import HallListView, HallDetailView, BookingCreateView, BookingSuccessView, MyBookingsView

urlpatterns = [
    path('', HallListView.as_view(), name='hall_list'),
    path('hall/<int:pk>/', HallDetailView.as_view(), name='hall_detail'),
    path('booking/new/', BookingCreateView.as_view(), name='booking_create'),
    path('booking/success/', BookingSuccessView.as_view(), name='booking_success'),
    path('my-bookings/', MyBookingsView.as_view(), name='my_bookings'),
]
