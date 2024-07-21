from django.urls import path
from .views import *

app_name = 'admins'

urlpatterns = [
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    
    path('managers/', ManagerListView.as_view(), name='manager_list'),
    path('managers/create/', ManagerCreateView.as_view(), name='manager_create'),
    path('managers/update/<int:pk>/', ManagerUpdateView.as_view(), name='manager_update'),
    path('managers/delete/<int:pk>/', ManagerDeleteView.as_view(), name='manager_delete'),

    path('receptionists/', ReceptionistListView.as_view(), name='receptionist_list'),
    path('receptionists/create/', ReceptionistCreateView.as_view(), name='receptionist_create'),
    path('receptionists/update/<int:pk>/', ReceptionistUpdateView.as_view(), name='receptionist_update'),
    path('receptionists/delete/<int:pk>/', ReceptionistDeleteView.as_view(), name='receptionist_delete'),

    # Category URLs
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
    path('categories/add/', CategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/update/', CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),

    # Room URLs
    path('rooms/', RoomListView.as_view(), name='room_list'),
    path('rooms/<int:pk>/', RoomDetailView.as_view(), name='room_detail'),
    path('rooms/add/', RoomCreateView.as_view(), name='room_add'),
    path('rooms/<int:pk>/update/', RoomUpdateView.as_view(), name='room_update'),
    path('rooms/<int:pk>/delete/', RoomDeleteView.as_view(), name='room_delete'),

    # Booking URLs
    path('bookings/', BookingListView.as_view(), name='booking_list'),
    path('bookings/<int:pk>/', BookingDetailView.as_view(), name='booking_detail'),
    path('bookings/add/', BookingCreateView.as_view(), name='booking_create'),
    path('bookings/<int:pk>/update/', BookingUpdateView.as_view(), name='booking_update'),
    path('bookings/<int:pk>/delete/', BookingDeleteView.as_view(), name='booking_delete'),
    path('booking/<int:pk>/extend/', BookingExtendView.as_view(), name='booking_extend'),
    

    
    # Payment URLs
    path('payments/', PaymentListView.as_view(), name='payment_list'),
    path('payment/create/<int:booking_id>/', PaymentCreateView.as_view(), name='payment_create'),
    path('payment/<int:booking_id>/extend/<int:pk>/update/', PaymentExtendView.as_view(), name='payment_extend_update'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment_detail'),
    path('payments/<int:pk>/delete/', PaymentDeleteView.as_view(), name='payment_delete'),

    path('membershipplans/', MembershipPlanListView.as_view(), name='membershipplan_list'),
    path('membershipplans/<int:pk>/', MembershipPlanDetailView.as_view(), name='membershipplan_detail'),
    path('membershipplans/create/', MembershipPlanCreateView.as_view(), name='membershipplan_create'),
    path('membershipplans/<int:pk>/update/', MembershipPlanUpdateView.as_view(), name='membershipplan_update'),
    path('membershipplans/<int:pk>/delete/', MembershipPlanDeleteView.as_view(), name='membershipplan_delete'),

    # Membership URLs
    path('memberships/create/', MembershipCreateView.as_view(), name='membership_create'),
    path('memberships/', MembershipListView.as_view(), name='membership_list'),
    path('memberships/<int:pk>/', MembershipDetailView.as_view(), name='membership_detail'),
    path('memberships/<int:pk>/update/', MembershipUpdateView.as_view(), name='membership_update'),
    path('memberships/<int:pk>/delete/', MembershipDeleteView.as_view(), name='membership_delete'),

    # MembershipPayment URLs
    path('membershippayments/', MembershipPaymentListView.as_view(), name='membershippayment_list'),
    path('membershippayments/<int:pk>/', MembershipPaymentDetailView.as_view(), name='membershippayment_detail'),
    path('membershippayments/<int:pk>/delete/', MembershipPaymentDeleteView.as_view(), name='membershippayment_delete'),

    
    
    # RoomRating URLs
    path('room_ratings/', RoomRatingListView.as_view(), name='room_rating_list'),
    path('room_ratings/<int:pk>/', RoomRatingDetailView.as_view(), name='room_rating_detail'),
    path('room_ratings/add/', RoomRatingCreateView.as_view(), name='room_rating_add'),
    path('room_ratings/<int:pk>/update/', RoomRatingUpdateView.as_view(), name='room_rating_update'),
    path('room_ratings/<int:pk>/delete/', RoomRatingDeleteView.as_view(), name='room_rating_delete'),

    
    # Hall URLs
    path('hall/create/', HallCreateView.as_view(), name='hall_create'),
    path('hall/<int:pk>/update/', HallUpdateView.as_view(), name='hall_update'),
    path('hall/<int:pk>/delete/', HallDeleteView.as_view(), name='hall_delete'),
    path('hall/<int:pk>/', HallDetailView.as_view(), name='hall_detail'),
    path('hall/', HallListView.as_view(), name='hall_list'),
    
    # Hall Booking URLs
    path('hall/availability/', HallAvailabilityView.as_view(), name='hall_availability'),
    path('hall/booking-create/<int:pk>/', HallBookingCreateView.as_view(), name='hall_booking_create'),
    path('hall_booking/<int:pk>/update/', HallBookingUpdateView.as_view(), name='hall_booking_update'),
    path('hall_booking/<int:pk>/delete/', HallBookingDeleteView.as_view(), name='hall_booking_delete'),
    path('hall_booking/', HallBookingListView.as_view(), name='hall_booking_list'),
    path('hall_booking/<int:pk>/', HallBookingDetailView.as_view(), name='hall_booking_detail'),

    # Hall Payment URLs
    path('hall_payment/<int:pk>/delete/', HallPaymentDeleteView.as_view(), name='hall_payment_delete'),
    path('hall_payment/', HallPaymentListView.as_view(), name='hall_payment_list'),
    path('hall-payment/<int:pk>/', HallPaymentDetailView.as_view(), name='hall_payment_detail'),
    path('hall/payment/<int:pk>/', HallPaymentCreateView.as_view(), name='hall_payment_create'),
    
    # SocialMediaPost URLs
    path('social_media_posts/', SocialMediaPostListView.as_view(), name='social_media_post_list'),
    path('social_media_posts/<int:pk>/', SocialMediaPostDetailView.as_view(), name='social_media_post_detail'),
    path('social_media_posts/add/', SocialMediaPostCreateView.as_view(), name='social_media_post_add'),
    path('social_media_posts/<int:pk>/update/', SocialMediaPostUpdateView.as_view(), name='social_media_post_update'),
    path('social_media_posts/<int:pk>/delete/', SocialMediaPostDeleteView.as_view(), name='social_media_post_delete'),

    # ChatMessage URLs
    path('chat_messages/', ChatMessageListView.as_view(), name='chat_message_list'),
    path('chat_messages/<int:pk>/', ChatMessageDetailView.as_view(), name='chat_message_detail'),
    path('chat_messages/add/', ChatMessageCreateView.as_view(), name='chat_message_add'),
    path('chat_messages/<int:pk>/update/', ChatMessageUpdateView.as_view(), name='chat_message_update'),
    # path('chat_messages/<int:pk>/delete/', ChatMessageDeleteView.as_view(), name='chat_message_delete'),

    
]
