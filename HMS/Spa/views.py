from django.views.generic import ListView, CreateView, View
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import SpaService, SpaPackage, SpaBooking
from .forms import SpaBookingForm

class ServiceListView(ListView):
    model = SpaService
    template_name = 'spa/spa_services_packages.html'
    context_object_name = 'services'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['packages'] = SpaPackage.objects.all()
        return context

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView

from .models import SpaService, SpaPackage, SpaBooking
from .forms import SpaBookingForm

class SpaBookingCreateView(LoginRequiredMixin, FormView):
    form_class = SpaBookingForm
    template_name = 'spa/spa_booking_create.html'

    def get(self, request, *args, **kwargs):
        item_type = self.kwargs.get('item_type')
        item_id = self.kwargs.get('item_id')

        if item_type == 'service':
            selected_item = SpaService.objects.filter(id=item_id).first()
        elif item_type == 'package':
            selected_item = SpaPackage.objects.filter(id=item_id).first()
        else:
            selected_item = None

        if selected_item is None:
            messages.error(request, 'The item you are trying to book does not exist.')
            return redirect('some_error_page')  # Redirect to an error page or the homepage

        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'item': selected_item})

    def post(self, request, *args, **kwargs):
        item_type = self.kwargs.get('item_type')
        item_id = self.kwargs.get('item_id')

        if item_type == 'service':
            selected_item = SpaService.objects.filter(id=item_id).first()
        elif item_type == 'package':
            selected_item = SpaPackage.objects.filter(id=item_id).first()
        else:
            selected_item = None

        if selected_item is None:
            messages.error(request, 'The item you are trying to book does not exist.')
            return redirect('some_error_page')  # Redirect to an error page or the homepage

        form = self.form_class(request.POST)
        if form.is_valid():
            appointment_date = form.cleaned_data['appointment_date']
            appointment_time = form.cleaned_data['appointment_time']

            existing_bookings_count = SpaBooking.objects.filter(
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                service=selected_item if item_type == 'service' else None,
                package=selected_item if item_type == 'package' else None
            ).count()

            if existing_bookings_count >= 5:
                messages.error(request, 'The selected time slot is fully booked. Please choose another time.')
                return render(request, self.template_name, {'form': form, 'item': selected_item})

            spa_booking = SpaBooking.objects.create(
                user=request.user,
                service=selected_item if item_type == 'service' else None,
                package=selected_item if item_type == 'package' else None,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                amount_due=selected_item.price,
                for_first_name=form.cleaned_data['first_name'] if form.cleaned_data['booking_for'] == 'others' else '',
                for_last_name=form.cleaned_data['last_name'] if form.cleaned_data['booking_for'] == 'others' else '',
                for_phone_number=form.cleaned_data['phone_number'] if form.cleaned_data['booking_for'] == 'others' else '',
                for_email=form.cleaned_data['email'] if form.cleaned_data['booking_for'] == 'others' else '',
                payment_method=form.cleaned_data['payment_method'],
                status='pending',
            )

            payment_method = form.cleaned_data['payment_method']
            if payment_method == 'chapa':
                return self.initiate_chapa_payment(spa_booking)
            elif payment_method == 'paypal':
                return self.initiate_paypal_payment(spa_booking)
            else:
                messages.error(request, 'Invalid payment method selected.')
                return render(request, self.template_name, {'form': form, 'item': selected_item})
        else:
            # Return form with errors
            return render(request, self.template_name, {'form': form, 'item': selected_item})

    def initiate_chapa_payment(self, spa_booking):
        # Your Chapa payment initiation logic here
        pass

    def initiate_paypal_payment(self, spa_booking):
        # Your PayPal payment initiation logic here
        pass




class BookingListView(LoginRequiredMixin, ListView):
    model = SpaBooking
    template_name = 'spa/booking_list.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return SpaBooking.objects.filter(user=self.request.user)

class CancelBookingView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        booking = SpaBooking.objects.get(id=kwargs['booking_id'], user=request.user)
        booking.status = 'cancelled'
        booking.save()
        return redirect('spa:booking_list')
