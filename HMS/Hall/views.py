# views.py
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .models import Hall, Hall_Booking
from django.views.generic import DetailView, FormView
from .models import Hall, Hall_Booking
from .forms import BookingForm
from django.shortcuts import redirect
from django.views.generic import CreateView
from .forms import BookingForm
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from .forms import CheckAvailabilityForm, BookingForm
import datetime


class HallListView(ListView):
    model = Hall
    template_name = 'hall/hall_list.html'

class HallDetailView(DetailView):
    model = Hall
    template_name = 'hall/hall_details.html'
    context_object_name = 'hall'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CheckAvailabilityForm()
        return context
class CheckAvailabilityView(FormView):
    form_class = CheckAvailabilityForm
    template_name = 'hall/hall_details.html'

    def form_valid(self, form):
        hall = Hall.objects.get(pk=self.kwargs['pk'])
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        start_time = form.cleaned_data['start_time']
        end_time = form.cleaned_data['end_time']

        availability = not Hall_Booking.objects.filter(
            hall=hall,
            start_date__lte=end_date if end_date else start_date,
            end_date__gte=start_date,
            start_time__lte=end_time,
            end_time__gte=start_time,
            status='confirmed'
        ).exists()

        if availability:
            # Store the form data in session
            self.request.session['booking_data'] = {
                'start_date': str(start_date),
                'end_date': str(end_date) if end_date else None,
                'start_time': str(start_time),
                'end_time': str(end_time)
            }
            return redirect(reverse_lazy('book_hall', kwargs={'pk': hall.pk}))
        else:
            context = {
                'form': form,
                'hall': hall,
                'availability': availability,
            }
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hall'] = Hall.objects.get(pk=self.kwargs['pk'])
        return context    

# views.py
from decimal import Decimal

class BookingView(TemplateView):
    template_name = 'hall/booking_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hall = get_object_or_404(Hall, pk=self.kwargs['pk'])
        booking_data = self.request.session.get('booking_data')

        if not booking_data:
            # Handle case where booking data is missing
            return redirect('hall_detail', pk=hall.pk)

        start_date = booking_data['start_date']
        end_date = booking_data.get('end_date')
        start_time = booking_data['start_time']
        end_time = booking_data['end_time']

        context.update({
            'hall': hall,
            'start_date': start_date,
            'end_date': end_date,
            'start_time': start_time,
            'end_time': end_time,
        })

        # Calculate total cost
        start_time_dt = datetime.datetime.strptime(start_time, '%H:%M:%S').time()
        end_time_dt = datetime.datetime.strptime(end_time, '%H:%M:%S').time()
        duration_hours = Decimal((datetime.datetime.combine(datetime.date.today(), end_time_dt) - datetime.datetime.combine(datetime.date.today(), start_time_dt)).seconds) / Decimal(3600)

        if end_date:
            days = (datetime.datetime.strptime(end_date, '%Y-%m-%d').date() - datetime.datetime.strptime(start_date, '%Y-%m-%d').date()).days + 1
            total_cost = duration_hours * hall.price_per_hour * Decimal(days)
        else:
            total_cost = duration_hours * hall.price_per_hour

        context['total_cost'] = total_cost
        return context

    def post(self, request, *args, **kwargs):
        hall = get_object_or_404(Hall, pk=self.kwargs['pk'])
        user = request.user
        booking_data = self.request.session.get('booking_data')

        if not booking_data:
            # Handle case where booking data is missing
            return redirect('hall_detail', pk=hall.pk)

        start_date = booking_data['start_date']
        end_date = booking_data.get('end_date')
        start_time = booking_data['start_time']
        end_time = booking_data['end_time']
        total_cost = self.get_context_data(**kwargs)['total_cost']

        # Create the booking
        booking = Hall_Booking.objects.create(
            user=user,
            hall=hall,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            amount_due=total_cost,
            is_paid=False,
            status='pending'
        )

        # Clear booking data from session
        del request.session['booking_data']

        return redirect('payment_page', pk=booking.pk, total_cost=total_cost)



    


class PaymentView(TemplateView):
    template_name = 'hall/payment_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = get_object_or_404(Hall_Booking, pk=self.kwargs['pk'])
        context['booking'] = booking
        context['total_cost'] = self.kwargs['total_cost']
        return context

    def post(self, request, *args, **kwargs):
        booking = get_object_or_404(Hall_Booking, pk=self.kwargs['pk'])
        booking.status = 'confirmed'
        booking.save()
        messages.success(request, 'Your booking has been confirmed.')
        return redirect('home')    
class BookingListView(ListView):
    model = Hall_Booking
    template_name = 'hall/my_bookings.html'  # Path to your template
    context_object_name = 'bookings'