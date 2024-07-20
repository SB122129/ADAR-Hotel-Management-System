from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from accountss.models import *
from room.models import *
from social_media.models import *
from .mixins import OwnerRequiredMixin
from django.shortcuts import render, redirect,get_object_or_404
from django import forms
from gym.models import *
from .forms import *
import random
import string
from django.db.models import Count, Sum, Avg, F, ExpressionWrapper, fields
from django.db.models.functions import TruncMonth,TruncDay
from datetime import timedelta
import json
from django.core.serializers.json import DjangoJSONEncoder

from datetime import datetime

def admin_dashboard(request):

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
        queryset = Booking.objects.all().order_by('-created_at')  # Changed from 'id' to '-created_at'
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

class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingCreateForm
    template_name = 'admins/booking_form.html'

    def form_valid(self, form):
        booking = form.save(commit=False)
        full_name = form.cleaned_data['full_name']
        booking.tx_ref = f"booking-{full_name.replace(' ', '')}-tx-{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}"
        booking.status = 'pending'
        
        if booking.check_in_date and booking.check_out_date:
            duration = (booking.check_out_date - booking.check_in_date).days
            booking.original_booking_amount = booking.room.price_per_night * duration
            booking.total_amount = booking.original_booking_amount
        booking.save()
        return redirect('admins:payment_create',booking_id=booking.id)



class BookingUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Booking
    template_name = 'admins/booking_update.html'
    form_class = BookingUpdateForm
    success_url = reverse_lazy('admins:booking_list')



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





from django.urls import reverse

class BookingExtendView(LoginRequiredMixin, UpdateView):
    model = Booking
    form_class = BookingExtendForm
    template_name = 'admins/booking_extend_form.html'

    def form_valid(self, form):
        booking = form.save(commit=False)
        additional_amount = booking.calculate_additional_amount()
        booking.booking_extend_amount = additional_amount
        booking.total_amount += additional_amount
        booking.status = 'pending'
        
        # Save the booking first
        booking.save()
        
        # Create or update the Payment object
        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={'amount': additional_amount}
        )
        
        if not created:
            # If the payment already exists, update it
            payment.amount = additional_amount
            payment.save()
        
        # Generate a new tx_ref for the payment
        full_name = booking.full_name
        booking.tx_ref = f"booking-{full_name.replace(' ', '')}-tx-{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}"
        booking.save()
        
        # Redirect to the payment extension view with booking and payment IDs
        return redirect(reverse('admins:payment_extend_update', kwargs={'booking_id': booking.id, 'pk': payment.id}))


# Room Payment Views

class PaymentExtendView(LoginRequiredMixin, UpdateView):
    model = Payment
    form_class = PaymentExtendForm
    template_name = 'admins/payment_extend_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = self.kwargs.get('booking_id')
        context['booking'] = get_object_or_404(Booking, pk=booking_id)
        return context

    def get_object(self):
        # Get the payment object based on the booking_id and the payment id
        booking_id = self.kwargs.get('booking_id')
        payment_id = self.kwargs.get('pk')  # 'pk' is used to get the payment instance
        booking = get_object_or_404(Booking, pk=booking_id)
        # Fetch or create a payment related to the booking if needed
        return get_object_or_404(Payment, id=payment_id, booking=booking)

    def form_valid(self, form):
        payment = form.save(commit=False)
        booking_id = self.kwargs.get('booking_id')
        booking = get_object_or_404(Booking, pk=booking_id)
        payment.booking = booking
        payment.amount = booking.booking_extend_amount  # Set amount manually
        payment.save()
        booking.status = 'confirmed'
        booking.check_out_date = booking.extended_check_out_date
        booking.save()
        messages.success(self.request, 'Booking and Payment for Extentsion completed')
        return redirect('admins:booking_list')

class PaymentCreateView(LoginRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentCreateForm
    template_name = 'admins/payment_form.html'
    success_url = reverse_lazy('admins:payment_list')

    def get_context_data(self, **kwargs):
        context = super(PaymentCreateView, self).get_context_data(**kwargs)
        booking_id = self.kwargs.get('booking_id')  
        context['booking'] = get_object_or_404(Booking, pk=booking_id)
        return context
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        booking_id = self.kwargs.get('booking_id')
        booking = get_object_or_404(Booking, pk=booking_id)
        kwargs.update({'initial': {'booking': booking}})
        return kwargs

    def form_valid(self, form):
        payment = form.save(commit=False)
        booking = get_object_or_404(Booking, pk=self.kwargs.get('booking_id'))
        payment.booking = booking
        payment.transaction_id = booking.tx_ref
        payment.payment_date = datetime.now()
        payment.save()
        booking.status = 'confirmed'
        booking.save()
        messages.success(self.request, 'Booking and Payment completed')
        return redirect(self.success_url)


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

