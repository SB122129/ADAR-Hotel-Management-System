# urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('', HallListView.as_view(), name='hall_list'),
    path('hall/<int:pk>/', HallDetailView.as_view(), name='hall_detail'),
    # path('my-bookings/', MyBookingsView.as_view(), name='my_bookings'),
    path('halls/<int:pk>/check-availability/', CheckAvailabilityView.as_view(), name='check_availability'),
    path('halls/<int:pk>/book/', BookingView.as_view(), name='book_hall'),
    path('payment/<int:pk>/<int:total_cost>/', PaymentView.as_view(), name='payment_page'),
]

