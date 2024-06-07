from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from accountss.models import *
from room.models import *
from social_media.models import *
from .mixins import OwnerRequiredMixin
from django.shortcuts import render
from django import forms

# Custom User Views
# class CustomUserListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
#     model = Custom_user
#     template_name = 'admins/custom_user_list.html'
#     context_object_name = 'users'

# class CustomUserDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
#     model = Custom_user
#     template_name = 'admins/custom_user_detail.html'

# class CustomUserCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
#     model = Custom_user
#     template_name = 'admins/custom_user_form.html'
#     fields = '__all__'
#     success_url = reverse_lazy('admins:custom_user_list')

# class CustomUserUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
#     model = Custom_user
#     template_name = 'admins/custom_user_form.html'
#     fields = '__all__'
#     success_url = reverse_lazy('admins:custom_user_list')

# class CustomUserDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
#     model = Custom_user
#     template_name = 'admins/custom_user_confirm_delete.html'
#     success_url = reverse_lazy('admins:custom_user_list')

# Language Views

from django.db.models import Count, Sum, Avg, F, ExpressionWrapper, fields
from django.db.models.functions import TruncMonth,TruncDay
from datetime import timedelta
import json
from django.core.serializers.json import DjangoJSONEncoder

from datetime import datetime

def admin_dashboard(request):
    # Room Availability with room types
    room_status_counts = list(Room.objects.values('room_status', 'room_type__name').annotate(count=Count('id')))
    room_status_data = [{'name': f"{item['room_status']} ({item['room_type__name']})", 'y': item['count']} for item in room_status_counts]

    # Booking Trends (per day)
    booking_trends = list(Booking.objects.annotate(day=TruncDay('check_in_date')).values('day').annotate(count=Count('id')))
    booking_trends_data = [
        {'x': int(datetime.combine(item['day'], datetime.min.time()).timestamp()) * 1000, 'y': item['count']}
        for item in booking_trends
    ]

    # Revenue Over Time (per day)
    revenue_trends = list(Booking.objects.filter(is_paid=True).annotate(day=TruncDay('check_in_date')).values('day').annotate(total_revenue=Sum('total_amount')))
    revenue_trends_data = [
        {'x': int(datetime.combine(item['day'], datetime.min.time()).timestamp()) * 1000, 'y': float(item['total_revenue'])}
        for item in revenue_trends
    ]

    # Booking Status Distribution with room types
    booking_status_counts = list(Booking.objects.values('status', 'room__room_type__name').annotate(count=Count('id')))
    booking_status_data = [{'name': f"{item['status']} ({item['room__room_type__name']})", 'y': item['count']} for item in booking_status_counts]

    # Payment Status Distribution with room types
    payment_status_counts = list(Payment.objects.values('status', 'booking__room__room_type__name').annotate(count=Count('id')))
    payment_status_data = [{'name': f"{item['status']} ({item['booking__room__room_type__name']})", 'y': item['count']} for item in payment_status_counts]

    # Room Type Popularity
    room_type_popularity = list(Booking.objects.values('room__room_type__name').annotate(count=Count('id')))
    room_type_popularity_data = [{'name': item['room__room_type__name'], 'y': item['count']} for item in room_type_popularity]

    # Revenue by Room Type
    revenue_by_room_type = list(Booking.objects.filter(is_paid=True).values('room__room_type__name').annotate(total_revenue=Sum('total_amount')))
    revenue_by_room_type_data = [
        {'name': item['room__room_type__name'], 'y': float(item['total_revenue'])}
        for item in revenue_by_room_type
    ]

    # Print JSON data for debugging
    print(json.dumps(room_status_data, cls=DjangoJSONEncoder))
    print(json.dumps(booking_trends_data, cls=DjangoJSONEncoder))
    print(json.dumps(revenue_trends_data, cls=DjangoJSONEncoder))
    print(json.dumps(booking_status_data, cls=DjangoJSONEncoder))
    print(json.dumps(payment_status_data, cls=DjangoJSONEncoder))
    print(json.dumps(room_type_popularity_data, cls=DjangoJSONEncoder))
    print(json.dumps(revenue_by_room_type_data, cls=DjangoJSONEncoder))

    context = {
        'room_status_data': json.dumps(room_status_data, cls=DjangoJSONEncoder),
        'booking_trends_data': json.dumps(booking_trends_data, cls=DjangoJSONEncoder),
        'revenue_trends_data': json.dumps(revenue_trends_data, cls=DjangoJSONEncoder),
        'booking_status_data': json.dumps(booking_status_data, cls=DjangoJSONEncoder),
        'payment_status_data': json.dumps(payment_status_data, cls=DjangoJSONEncoder),
        'room_type_popularity_data': json.dumps(room_type_popularity_data, cls=DjangoJSONEncoder),
        'revenue_by_room_type_data': json.dumps(revenue_by_room_type_data, cls=DjangoJSONEncoder),
    }

    return render(request, 'admins/admin_dashboard.html', context)

    

class LanguageListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = Language
    template_name = 'admins/language_list.html'
    context_object_name = 'languages'
    def get_queryset(self):
        return Language.objects.order_by('name')


class LanguageDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Language
    template_name = 'admins/language_detail.html'

class LanguageCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
    model = Language
    template_name = 'admins/language_form.html'
    fields = '__all__'
    success_url = reverse_lazy('admins:language_list')

class LanguageUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Language
    template_name = 'admins/language_form.html'
    fields = '__all__'
    success_url = reverse_lazy('admins:language_list')

class LanguageDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Language
    template_name = 'admins/language_confirm_delete.html'
    success_url = reverse_lazy('admins:language_list')

# Category Views
class CategoryListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = Category
    template_name = 'admins/category_list.html'
    context_object_name = 'categories'
    def get_queryset(self):
        return Category.objects.order_by('name')

class CategoryDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Category
    template_name = 'admins/category_detail.html'

class CategoryCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
    model = Category
    template_name = 'admins/category_form.html'
    fields = '__all__'
    success_url = reverse_lazy('admins:category_list')

class CategoryUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Category
    template_name = 'admins/category_form.html'
    fields = '__all__'
    success_url = reverse_lazy('admins:category_list')

class CategoryDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Category
    template_name = 'admins/category_confirm_delete.html'
    success_url = reverse_lazy('admins:category_list')

# Room Views
class RoomListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = Room
    template_name = 'admins/room_list.html'
    context_object_name = 'rooms'
    def get_queryset(self):
        return Room.objects.order_by('id')


class RoomDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Room
    template_name = 'admins/room_detail.html'

class RoomCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
    model = Room
    template_name = 'admins/room_form.html'
    fields = '__all__'
    success_url = reverse_lazy('admins:room_list')

class RoomUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Room
    template_name = 'admins/room_form.html'
    fields = '__all__'
    success_url = reverse_lazy('admins:room_list')

class RoomDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Room
    template_name = 'admins/room_confirm_delete.html'
    success_url = reverse_lazy('admins:room_list')

# Booking Views
class BookingListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = Booking
    template_name = 'admins/booking_list.html'
    context_object_name = 'bookings'
    def get_queryset(self):
        return Booking.objects.order_by('id')


class BookingDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Booking
    template_name = 'admins/booking_detail.html'

class BookingCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
    model = Booking
    template_name = 'admins/booking_form.html'
    fields = '__all__'
    success_url = reverse_lazy('admins:booking_list')


class BookingUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Booking
    template_name = 'admins/booking_form.html'
    success_url = reverse_lazy('admins:booking_list')

class BookingDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Booking
    template_name = 'admins/booking_confirm_delete.html'
    success_url = reverse_lazy('admins:booking_list')

# Reservation Views
class ReservationListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = Reservation
    template_name = 'admins/reservation_list.html'
    context_object_name = 'reservations'
    def get_queryset(self):
        return Category.objects.order_by('name')


class ReservationDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Reservation
    template_name = 'admins/reservation_detail.html'

class ReservationCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
    model = Reservation
    template_name = 'admins/reservation_form.html'
    fields = '__all__'
    success_url = reverse_lazy('admins:reservation_list')

class ReservationUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Reservation
    template_name = 'admins/reservation_form.html'
    fields = '__all__'
    success_url = reverse_lazy('admins:reservation_list')

class ReservationDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Reservation
    template_name = 'admins/reservation_confirm_delete.html'
    success_url = reverse_lazy('admins:reservation_list')

# Payment Views
class PaymentListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = Payment
    template_name = 'admins/payment_list.html'
    context_object_name = 'payments'
    def get_queryset(self):
        return Payment.objects.order_by('id')


class PaymentDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Payment
    template_name = 'admins/payment_detail.html'

class PaymentCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
    model = Payment
    template_name = 'admins/payment_form.html'
    fields = '__all__'
    success_url = reverse_lazy('admins:payment_list')

class PaymentUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Payment
    template_name = 'admins/payment_form.html'
    fields = '__all__'
    success_url = reverse_lazy('admins:payment_list')

class PaymentDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Payment
    template_name = 'admins/payment_confirm_delete.html'
    success_url = reverse_lazy('admins:payment_list')

# RoomRating Views
class RoomRatingListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = RoomRating
    template_name = 'admins/room_rating_list.html'
    context_object_name = 'room_ratings'
    def get_queryset(self):
        return Category.objects.order_by('name')


class RoomRatingDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = RoomRating
    template_name = 'admins/room_rating_detail.html'

class RoomRatingCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
    model = RoomRating
    template_name = 'admins/room_rating_form.html'
    fields = '__all__'
    success_url = reverse_lazy('admins:room_rating_list')

class RoomRatingUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = RoomRating
    template_name = 'admins/room_rating_form.html'
    fields = '__all__'
    success_url = reverse_lazy('admins:room_rating_list')

class RoomRatingDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = RoomRating
    template_name = 'admins/room_rating_confirm_delete.html'
    success_url = reverse_lazy('admins:room_rating_list')

# SocialMediaPost Views
class SocialMediaPostListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = SocialMediaPost
    template_name = 'admins/social_media_post_list.html'
    context_object_name = 'social_media_posts'
    def get_queryset(self):
        return Category.objects.order_by('name')


class SocialMediaPostDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = SocialMediaPost
    template_name = 'admins/social_media_post_detail.html'

class SocialMediaPostCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
    model = SocialMediaPost
    template_name = 'admins/social_media_post_form.html'
    fields = '__all__'
    success_url = reverse_lazy('admins:social_media_post_list')

class SocialMediaPostUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = SocialMediaPost
    template_name = 'admins/social_media_post_form.html'
    fields = '__all__'
    success_url = reverse_lazy('admins:social_media_post_list')

class SocialMediaPostDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = SocialMediaPost
    template_name = 'admins/social_media_post_confirm_delete.html'
    success_url = reverse_lazy('admins:social_media_post_list')

# ChatMessage Views
class ChatMessageListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = ChatMessage
    template_name = 'admins/chat_message_list.html'
    context_object_name = 'chat_messages'
    def get_queryset(self):
        return Category.objects.order_by('name')


class ChatMessageDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = ChatMessage
    template_name = 'admins/chat_message_detail.html'

class ChatMessageCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
    model = ChatMessage
    template_name = 'admins/chat_message_form.html'
    fields = '__all__'
    success_url = reverse_lazy('admins:chat_message_list')

class ChatMessageUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = ChatMessage
    template_name = 'admins/chat_message_form.html'
    fields = '__all__'
    success_url = reverse_lazy('admins:chat_message_list')

class ChatMessageDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = ChatMessage
    template_name = 'admins/chat_message_confirm_delete.html'
    success_url = reverse_lazy('admins:chat_message_list')

# ChatBot Views
class ChatBotListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = ChatBot
    template_name = 'admins/chat_bot_list.html'
    context_object_name = 'chat_bots'
    def get_queryset(self):
        return Category.objects.order_by('name')


class ChatBotDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = ChatBot
    template_name = 'admins/chat_bot_detail.html'

class ChatBotCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
    model = ChatBot
    template_name = 'admins/chat_bot_form.html'
    fields = '__all__'
    success_url = reverse_lazy('admins:chat_bot_list')

class ChatBotUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = ChatBot
    template_name = 'admins/chat_bot_form.html'
    fields = '__all__'
    success_url = reverse_lazy('admins:chat_bot_list')

class ChatBotDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = ChatBot
    template_name = 'admins/chat_bot_confirm_delete.html'
    success_url = reverse_lazy('admins:chat_bot_list')
