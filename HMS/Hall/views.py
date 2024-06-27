# views.py

from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .models import Hall, Hall_Booking
from .forms import BookingForm

class HallListView(ListView):
    model = Hall
    template_name = 'hall_list.html'

class HallDetailView(DetailView):
    model = Hall
    template_name = 'hall_detail.html'

class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Hall_Booking
    form_class = BookingForm
    template_name = 'booking_form.html'
    success_url = reverse_lazy('booking_success')

    def form_valid(self, form):
        form.instance.user = self.request.user
        # Calculate amount due
        hall = form.cleaned_data['hall']
        start_time = form.cleaned_data['start_time']
        end_time = form.cleaned_data['end_time']
        hours = (end_time - start_time).seconds // 3600
        form.instance.amount_due = hours * hall.price_per_hour
        return super().form_valid(form)

class BookingSuccessView(TemplateView):
    template_name = 'booking_success.html'

class MyBookingsView(LoginRequiredMixin, ListView):
    model = Hall_Booking
    template_name = 'my_bookings.html'

    def get_queryset(self):
        return Hall_Booking.objects.filter(user=self.request.user)
