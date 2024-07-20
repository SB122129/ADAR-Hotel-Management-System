from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView,TemplateView, DetailView,FormView, CreateView, UpdateView, DeleteView
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




from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from Hall.models import Hall, Hall_Booking, Hall_Payment
from .forms import HallForm, HallBookingForm, HallPaymentForm

# Hall Views
class HallCreateView(CreateView):
    model = Hall
    form_class = HallForm
    template_name = 'admins/hall_form.html'
    success_url = reverse_lazy('admins:hall_list')

class HallDetailView(DetailView):
    model = Hall
    template_name = 'admins/hall_detail.html'
class HallUpdateView(UpdateView):
    model = Hall
    form_class = HallForm
    template_name = 'admins/hall_form.html'
    success_url = reverse_lazy('admins:hall_list')

class HallDeleteView(DeleteView):
    model = Hall
    template_name = 'admins/hall_confirm_delete.html'
    success_url = reverse_lazy('admins:hall_list')

class HallListView(ListView):
    model = Hall
    template_name = 'admins/hall_list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = Hall.objects.all().order_by('hall_number')  # Adjust ordering as needed
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(hall_number__icontains=search_query) |
                Q(hall_type__name__icontains=search_query)  # Assuming hall_type is a CharField or similar
            )
        return queryset

# Hall Booking Views
class HallAvailabilityView(FormView):
    form_class = CheckAvailabilityForm
    template_name = 'admins/hall_availability.html'

    def form_valid(self, form):
        hall = form.cleaned_data['hall']
        start_date = form.cleaned_data['start_date'].strftime('%Y-%m-%d')
        end_date = form.cleaned_data['end_date'].strftime('%Y-%m-%d') if form.cleaned_data['end_date'] else start_date
        start_time = form.cleaned_data['start_time'].strftime('%H:%M:%S')
        end_time = form.cleaned_data['end_time'].strftime('%H:%M:%S')

        conflicting_bookings = Hall_Booking.objects.filter(
            hall=hall,
            status='confirmed'
        ).filter(
            Q(start_date__lte=end_date) & Q(end_date__gte=start_date) &
            Q(start_time__lte=end_time) & Q(end_time__gte=start_time)
        )

        availability = not conflicting_bookings.exists()
        context = {
            'form': form,
            'hall': hall,
            'availability': availability,
        }

        if availability:
            # Store booking data in session with string conversion
            self.request.session['booking_data'] = {
                'start_date': start_date,
                'end_date': end_date,
                'start_time': start_time,
                'end_time': end_time,
            }
            return redirect('admins:hall_booking_create', pk=hall.pk)  # Redirect to booking create view

        return self.render_to_response(context)


# views.py (in HallBookingCreateView)

from datetime import datetime

class HallBookingCreateView(TemplateView):
    template_name = 'admins/hall_booking_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hall = get_object_or_404(Hall, pk=self.kwargs['pk'])
        booking_data = self.request.session.get('booking_data')

        if not booking_data:
            # Handle case where booking data is missing
            return redirect('admins:hall_availability')

        start_date = booking_data['start_date']
        end_date = booking_data.get('end_date')
        start_time = booking_data['start_time']
        end_time = booking_data['end_time']

        # Calculate total cost
        start_time_dt = datetime.strptime(start_time, '%H:%M:%S').time()
        end_time_dt = datetime.strptime(end_time, '%H:%M:%S').time()
        today = date.today()  # Correct usage of date.today()

        duration_hours = Decimal((datetime.combine(today, end_time_dt) - datetime.combine(today, start_time_dt)).seconds) / Decimal(3600)

        if end_date:
            days = (datetime.strptime(end_date, '%Y-%m-%d').date() - datetime.strptime(start_date, '%Y-%m-%d').date()).days + 1
            total_cost = duration_hours * hall.price_per_hour * Decimal(days)
        else:
            total_cost = duration_hours * hall.price_per_hour

        context.update({
            'hall': hall,
            'start_date': start_date,
            'end_date': end_date,
            'start_time': start_time_dt,
            'end_time': end_time_dt,
            'total_cost': total_cost,
        })

        return context

    def post(self, request, *args, **kwargs):
        hall = get_object_or_404(Hall, pk=self.kwargs['pk'])
        user = request.user
        booking_data = self.request.session.get('booking_data')

        if not booking_data:
            # Handle case where booking data is missing
            return redirect('admins:hall_availability')

        start_date = booking_data['start_date']
        end_date = booking_data.get('end_date')
        start_time = booking_data['start_time']
        end_time = booking_data['end_time']
        total_cost = self.get_context_data(**kwargs)['total_cost']
        full_name = request.POST.get('full_name')

        # Create the booking
        booking = Hall_Booking.objects.create(
            hall=hall,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            amount_due=total_cost,
            status='pending',
            full_name=full_name  # Save the full name to the booking
        )

        # Clear booking data from session
        del request.session['booking_data']

        return redirect('admins:hall_payment_create', pk=booking.pk)



class HallCreatePaymentView(TemplateView):
    template_name = 'admins/hall_payment_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = get_object_or_404(Hall_Booking, pk=self.kwargs['pk'])
        context['booking'] = booking
        context['payment_methods'] = Hall_Payment.PAYMENT_METHOD_CHOICES
        return context

    def post(self, request, *args, **kwargs):
        booking = get_object_or_404(Hall_Booking, pk=self.kwargs['pk'])
        payment_method = request.POST.get('payment_method')

        if payment_method not in dict(Hall_Payment.PAYMENT_METHOD_CHOICES).keys():
            messages.error(request, 'Invalid payment method selected.')
            return render(request, self.template_name, self.get_context_data())

        # Create the payment instance
        payment = Hall_Payment.objects.create(
            booking=booking,
            payment_method=payment_method,
            transaction_id=self.generate_transaction_id(),
        )

        # For simplicity, let's assume cash payments are completed immediately
        if payment_method == 'cash':
            payment.status = 'completed'
            payment.save()
            messages.success(request, 'Cash payment has been successfully processed.')
            return redirect('admins:hall_booking_list')

        # Redirect to a success page or update the booking status as needed
        messages.success(request, f'{payment_method.capitalize()} payment method selected.')
        return redirect('admins:hall_booking_list')

    def generate_transaction_id(self):
        """Generate a unique transaction ID."""
        import random
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

class HallBookingDetailView(DetailView):
    model = Hall_Booking
    template_name = 'admins/hall_booking_detail.html'
    context_object_name = 'object'

class HallBookingUpdateView(UpdateView):
    model = Hall_Booking
    form_class = HallBookingUpdateForm
    template_name = 'admins/hall_booking_update_form.html'
    success_url = reverse_lazy('admins:hall_booking_list')

class HallBookingDeleteView(DeleteView):
    model = Hall_Booking
    template_name = 'admins/hall_booking_confirm_delete.html'
    success_url = reverse_lazy('admins:hall_booking_list')

class HallBookingListView(ListView):
    model = Hall_Booking
    template_name = 'admins/hall_booking_list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = Hall_Booking.objects.all().order_by('-created_at')  # Adjust as needed
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(hall__hall_number__icontains=search_query) |
                Q(hall__hall_type__name__icontains=search_query) |
                Q(tx_ref__icontains=search_query)  # Adjust this field as needed
            )
        return queryset

# Hall Payment Views
class HallPaymentCreateView(CreateView):
    model = Hall_Payment
    form_class = HallPaymentForm
    template_name = 'admins/hall_payment_form.html'
    success_url = reverse_lazy('admins:hall_payment_list')

class HallPaymentUpdateView(UpdateView):
    model = Hall_Payment
    form_class = HallPaymentForm
    template_name = 'admins/hall_payment_form.html'
    success_url = reverse_lazy('admins:hall_payment_list')

class HallPaymentDeleteView(DeleteView):
    model = Hall_Payment
    template_name = 'admins/hall_payment_confirm_delete.html'
    success_url = reverse_lazy('admins:hall_payment_list')

class HallPaymentDetailView(DetailView):
    model = Hall_Payment
    template_name = 'admins/hall_payment_detail.html'
    context_object_name = 'payment'

class HallPaymentListView(ListView):
    model = Hall_Payment
    template_name = 'admins/hall_payment_list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = Hall_Payment.objects.all().order_by('-payment_date')
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(transaction_id__icontains=search_query) |
                Q(status__icontains=search_query)
            )
        return queryset





















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

