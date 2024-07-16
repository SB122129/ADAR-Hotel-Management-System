from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from accountss.models import *
from room.models import *
from social_media.models import *
from .mixins import OwnerRequiredMixin
from django.shortcuts import render
from django import forms
from gym.models import *
from .forms import *


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

    # Room Type Popularity
    room_type_popularity = list(Booking.objects.values('room__room_type__name').annotate(count=Count('id')))
    room_type_popularity_data = [{'name': item['room__room_type__name'], 'y': item['count']} for item in room_type_popularity]

    # Revenue by Room Type
    revenue_by_room_type = list(Booking.objects.filter(is_paid=True).values('room__room_type__name').annotate(total_revenue=Sum('total_amount')))
    revenue_by_room_type_data = [
        {'name': item['room__room_type__name'], 'y': float(item['total_revenue'])}
        for item in revenue_by_room_type
    ]

    context = {
        'booking_trends_data': json.dumps(booking_trends_data, cls=DjangoJSONEncoder),
        'revenue_trends_data': json.dumps(revenue_trends_data, cls=DjangoJSONEncoder),
        'room_type_popularity_data': json.dumps(room_type_popularity_data, cls=DjangoJSONEncoder),
        'revenue_by_room_type_data': json.dumps(revenue_by_room_type_data, cls=DjangoJSONEncoder),
    }

    return render(request, 'admins/admin_dashboard.html', context)


    


# Category Views
class CategoryListView(ListView):
    model = Category
    template_name = 'admins/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('search')
        if query:
            return Category.objects.filter(name__icontains=query)
        return Category.objects.order_by('name')

class CategoryDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Category
    template_name = 'admins/category_detail.html'



class CategoryCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
    model = Category
    template_name = 'admins/category_form.html'
    form_class = CategoryForm
    success_url = reverse_lazy('admins:category_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Category created successfully.')
        return response

class CategoryUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Category
    template_name = 'admins/category_form.html'
    form_class = CategoryForm
    success_url = reverse_lazy('admins:category_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Category updated successfully.')
        return response

class CategoryDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Category
    template_name = 'admins/category_confirm_delete.html'
    success_url = reverse_lazy('admins:category_list')

# Room Views
class RoomListView(ListView):
    model = Room
    template_name = 'admins/room_list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = Room.objects.all().order_by('id')
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(Q(room_number__icontains=search_query) | Q(room_type__name__icontains=search_query))
        return queryset


class RoomDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Room
    template_name = 'admins/room_detail.html'

class RoomCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
    model = Room
    template_name = 'admins/room_form.html'
    form_class = RoomForm
    success_url = reverse_lazy('admins:room_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Room created successfully.')
        return response

class RoomUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Room
    template_name = 'admins/room_form.html'
    form_class = RoomForm
    success_url = reverse_lazy('admins:room_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Room updated successfully.')
        return response

class RoomDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Room
    template_name = 'admins/room_confirm_delete.html'
    success_url = reverse_lazy('admins:room_list')




# Booking Views
from django.views.generic import ListView
from django.db.models import Q
from room.models import Booking

class BookingListView(ListView):
    model = Booking
    template_name = 'admins/booking_list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = Booking.objects.all().order_by('id')
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(room__room_number__icontains=search_query) |
                Q(room__room_type__name__icontains=search_query) |
                Q(user__username__icontains=search_query) |
                Q(tx_ref__icontains=search_query)
            )
        return queryset



class BookingDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Booking
    template_name = 'admins/booking_detail.html'


class BookingDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Booking
    template_name = 'admins/booking_confirm_delete.html'
    success_url = reverse_lazy('admins:booking_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        try:
            self.object.delete()
            messages.success(self.request, 'Booking successfully deleted.')
        except Exception as e:
            messages.error(self.request, f'Failed to delete booking: {str(e)}')
        return super().delete(request, *args, **kwargs)



# Room Payment Views

class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'admins/payment_list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = Payment.objects.all().order_by('id')
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(booking__room__room_number__icontains=search_query) |
                Q(booking__room__room_type__name__icontains=search_query) |
                Q(booking__user__username__icontains=search_query) |
                Q(transaction_id__icontains=search_query)
            )
        return queryset



class PaymentDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Payment
    template_name = 'admins/payment_detail.html'



class PaymentDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Payment
    template_name = 'admins/payment_confirm_delete.html'
    success_url = reverse_lazy('admins:payment_list')





from .forms import MembershipPlanForm, MembershipForm, MembershipPaymentForm

# MembershipPlan Views
class MembershipPlanListView(ListView):
    model = MembershipPlan
    template_name = 'admins/membershipplan_list.html'
    context_object_name = 'membershipplans'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('search')
        if query:
            return MembershipPlan.objects.filter(name__icontains=query)
        return MembershipPlan.objects.order_by('name')

class MembershipPlanDetailView(LoginRequiredMixin, DetailView):
    model = MembershipPlan
    template_name = 'admins/membershipplan_detail.html'

class MembershipPlanCreateView(LoginRequiredMixin, CreateView):
    model = MembershipPlan
    template_name = 'admins/membershipplan_form.html'
    form_class = MembershipPlanForm
    success_url = reverse_lazy('admins:membershipplan_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Membership Plan created successfully.')
        return response

class MembershipPlanUpdateView(LoginRequiredMixin, UpdateView):
    model = MembershipPlan
    template_name = 'admins/membershipplan_form.html'
    form_class = MembershipPlanForm
    success_url = reverse_lazy('admins:membershipplan_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Membership Plan updated successfully.')
        return response

class MembershipPlanDeleteView(LoginRequiredMixin, DeleteView):
    model = MembershipPlan
    template_name = 'admins/membershipplan_confirm_delete.html'
    success_url = reverse_lazy('admins:membershipplan_list')

# Membership Views
class MembershipListView(ListView):
    model = Membership
    template_name = 'admins/membership_list.html'
    context_object_name = 'memberships'
    paginate_by = 10

    def get_queryset(self):
        queryset = Membership.objects.all().order_by('id')
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(plan__name__icontains=search_query) |
                Q(tx_ref__icontains=search_query)
            )
        return queryset

class MembershipDetailView(LoginRequiredMixin, DetailView):
    model = Membership
    template_name = 'admins/membership_detail.html'



class MembershipDeleteView(LoginRequiredMixin, DeleteView):
    model = Membership
    template_name = 'admins/membership_confirm_delete.html'
    success_url = reverse_lazy('admins:membership_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        try:
            self.object.delete()
            messages.success(self.request, 'Membership successfully deleted.')
        except Exception as e:
            messages.error(self.request, f'Failed to delete membership: {str(e)}')
        return super().delete(request, *args, **kwargs)

# MembershipPayment Views
class MembershipPaymentListView(LoginRequiredMixin, ListView):
    model = MembershipPayment
    template_name = 'admins/membershippayment_list.html'
    context_object_name = 'membershippayments'
    paginate_by = 10

    def get_queryset(self):
        queryset = MembershipPayment.objects.all().order_by('id')
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(membership__user__username__icontains=search_query) |
                Q(membership__plan__name__icontains=search_query) |
                Q(transaction_id__icontains=search_query)
            )
        return queryset

class MembershipPaymentDetailView(LoginRequiredMixin, DetailView):
    model = MembershipPayment
    template_name = 'admins/membershippayment_detail.html'

class MembershipPaymentCreateView(LoginRequiredMixin, CreateView):
    model = MembershipPayment
    template_name = 'admins/membershippayment_form.html'
    form_class = MembershipPaymentForm
    success_url = reverse_lazy('admins:membershippayment_list')

class MembershipPaymentUpdateView(LoginRequiredMixin, UpdateView):
    model = MembershipPayment
    template_name = 'admins/membershippayment_form.html'
    form_class = MembershipPaymentForm
    success_url = reverse_lazy('admins:membershippayment_list')

class MembershipPaymentDeleteView(LoginRequiredMixin, DeleteView):
    model = MembershipPayment
    template_name = 'admins/membershippayment_confirm_delete.html'
    success_url = reverse_lazy('admins:membershippayment_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        try:
            self.object.delete()
            messages.success(self.request, 'Membership Payment successfully deleted.')
        except Exception as e:
            messages.error(self.request, f'Failed to delete membership payment: {str(e)}')
        return super().delete(request, *args, **kwargs)








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

