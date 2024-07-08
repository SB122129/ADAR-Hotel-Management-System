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
    template_name = 'check_availability.html'

    def form_valid(self, form):
        hall = Hall.objects.get(pk=self.kwargs['pk'])
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        start_time = form.cleaned_data['start_time']
        end_time = form.cleaned_data['end_time']

        availability = not Booking.objects.filter(
            hall=hall,
            start_date__lte=end_date if end_date else start_date,
            end_date__gte=start_date,
            start_time__lte=end_time,
            end_time__gte=start_time,
            status='confirmed'
        ).exists()

        context = {
            'hall': hall,
            'availability': availability
        }
        return self.render_to_response(context)    

class BookingView(CreateView):
    form_class = BookingForm
    template_name = 'booking_create.html'

    def form_valid(self, form):
        booking = form.save(commit=False)
        booking.user = self.request.user
        hall = Hall.objects.get(pk=self.kwargs['pk'])
        booking.hall = hall

        # Calculate the cost
        duration = (booking.end_time.hour - booking.start_time.hour)
        cost_per_hour = 100  # Example cost per hour
        total_cost = duration * cost_per_hour

        booking.status = 'pending'
        booking.save()

        # Redirect to payment page with total_cost
        return redirect('payment_create', booking.pk, total_cost)
    


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
