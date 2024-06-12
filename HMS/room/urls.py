from django.urls import path
from .views import *

urlpatterns = [
    path('', RoomListView.as_view(), name='rooms'),
    path('<int:pk>/', RoomDetailView.as_view(), name='room_detail'),
     path('my-bookings/', BookingListView.as_view(), name='bookings'),
    path('<int:room_id>/book/', BookingCreateView.as_view(), name='booking_create'),
    path('<int:room_id>/reserve/', ReservationCreateView.as_view(), name='reservation_create'),
    path('booking/<int:booking_id>/pay/', PaymentView.as_view(), name='payment_create'),
    # path('booking/<int:booking_id>/pays/', payment_view2, name='payment'),
    #path('/<int:room_id>/rate/', RoomRatingCreateView.as_view(), name='room_rating_create'),
    #path('payment_details/', PaymentDetailsView.as_view(), name='payment_details'),
    path('booking/extend/<int:booking_id>/', BookingExtendView.as_view(), name='booking_extend'),
    path('payment/extend/<int:booking_id>/', PaymentExtendView.as_view(), name='payment_extend'),
    path('booking/delete/<int:pk>/', BookingDeleteView.as_view(), name='booking_delete'),
    path('chapa-webhook/', ChapaWebhookView.as_view(), name='chapa_webhook'),
    path('booking/<int:booking_id>/upload_receipt/', ReceiptUploadView.as_view(), name='upload_receipt'),
    path('paypal-return/', PayPalReturnView.as_view(), name='paypal_return'),
    path('paypal-cancel/', PayPalCancelView.as_view(), name='paypal_cancel'),
]
