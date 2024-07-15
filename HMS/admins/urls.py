from django.urls import path
from .views import *

app_name = 'admins'

urlpatterns = [
    # # CustomUser URLs
    # path('users/', CustomUserListView.as_view(), name='custom_user_list'),
    # path('users/<int:pk>/', CustomUserDetailView.as_view(), name='custom_user_detail'),
    # path('users/add/', CustomUserCreateView.as_view(), name='custom_user_add'),
    # path('users/<int:pk>/update/', CustomUserUpdateView.as_view(), name='custom_user_update'),
    # path('users/<int:pk>/delete/', CustomUserDeleteView.as_view(), name='custom_user_delete'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    # Language URLs
    path('languages/', LanguageListView.as_view(), name='language_list'),
    path('languages/<int:pk>/', LanguageDetailView.as_view(), name='language_detail'),
    path('languages/add/', LanguageCreateView.as_view(), name='language_add'),
    path('languages/<int:pk>/update/', LanguageUpdateView.as_view(), name='language_update'),
    path('languages/<int:pk>/delete/', LanguageDeleteView.as_view(), name='language_delete'),

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
    path('bookings/add/', BookingCreateView.as_view(), name='booking_add'),
    path('bookings/<int:pk>/update/', BookingUpdateView.as_view(), name='booking_update'),
    path('bookings/<int:pk>/delete/', BookingDeleteView.as_view(), name='booking_delete'),

    
    # Payment URLs
    path('payments/', PaymentListView.as_view(), name='payment_list'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment_detail'),
    path('payments/add/', PaymentCreateView.as_view(), name='payment_add'),
    path('payments/<int:pk>/update/', PaymentUpdateView.as_view(), name='payment_update'),
    path('payments/<int:pk>/delete/', PaymentDeleteView.as_view(), name='payment_delete'),

    # RoomRating URLs
    path('room_ratings/', RoomRatingListView.as_view(), name='room_rating_list'),
    path('room_ratings/<int:pk>/', RoomRatingDetailView.as_view(), name='room_rating_detail'),
    path('room_ratings/add/', RoomRatingCreateView.as_view(), name='room_rating_add'),
    path('room_ratings/<int:pk>/update/', RoomRatingUpdateView.as_view(), name='room_rating_update'),
    path('room_ratings/<int:pk>/delete/', RoomRatingDeleteView.as_view(), name='room_rating_delete'),

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
    path('chat_messages/<int:pk>/delete/', ChatMessageDeleteView.as_view(), name='chat_message_delete'),

    # ChatBot URLs
    # path('chat_bots/', ChatBotListView.as_view(), name='chat_bot_list'),
    # path('chat_bots/<int:pk>/', ChatBotDetailView.as_view(), name='chat_bot_detail'),
    # path('chat_bots/add/', ChatBotCreateView.as_view(), name='chat_bot_add'),
    # path('chat_bots/<int:pk>/update/', ChatBotUpdateView.as_view(), name='chat_bot_update'),
    # path('chat_bots/<int:pk>/delete/', ChatBotDeleteView.as_view(), name='chat_bot_delete'),
]
