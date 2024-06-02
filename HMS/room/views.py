from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Room, Booking, Reservation, Payment, RoomRating,Receipt
from .forms import BookingForm, ReservationForm, RoomRatingForm
import requests
import random
import string
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.dispatch import receiver
import requests
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic.edit import FormView
from .models import Payment, Booking
from django.contrib.sites.models import Site
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from django.utils import timezone
from django.contrib import messages
from django.views.generic.base import View
from django.db.models.signals import post_save




def home(request):
    rooms = Room.objects.available().filter(room_status='vacant').order_by('room_type', 'id').distinct('room_type')
    print(rooms)
    return render(request, 'room/home.html', {'rooms': rooms})

class RoomListView(ListView):
    model = Room
    template_name = 'room/rooms.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        return Room.objects.available()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        return context

def about(request):
    return render(request, 'room/about.html')


def contact(request):
    return render(request, 'room/contact.html')


class RoomDetailView(DetailView):
    model = Room
    template_name = 'room/room_detail.html'
    context_object_name = 'room'


class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'room/reservation_create.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'room/bookings.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)



class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'room/booking_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = get_object_or_404(Room, id=self.kwargs['room_id'])
        context['room_image'] = room.room_image
        context['room_number'] = room.room_number  # Assuming 'number' is the field for room number
        context['room_type'] = room.room_type  # Assuming 'type' is the field for room type
        return context
    def form_valid(self, form):
        room = get_object_or_404(Room, id=self.kwargs['room_id'])
        form.instance.user = self.request.user
        form.instance.room = room
        form.instance.status = 'pending'
        self.object = form.save()
        return redirect('payment_create', booking_id=self.object.id)
    
    def form_invalid(self, form):
        print("Form is invalid")
        print(form.errors)  # Print form errors to the console for debugging
        return self.render_to_response(self.get_context_data(form=form))





class PaymentView(View):
    template_name = 'room/payment_create.html'
    success_url = reverse_lazy('bookings')

    def dispatch(self, request, *args, **kwargs):
        self.booking = self.get_booking()
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = {}
        context['booking'] = self.booking
        context['user'] = self.booking.user
        context['amount'] = self.booking.total_amount
        context['data'] = {
            "customization": {
                "title": "Payment for my booking",
                "description": "Confirming my booking"
            }
        }
        return context
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())
    
    def post(self, request, *args, **kwargs):
        amount = str(self.booking.total_amount)
        tx_ref = f"{self.booking.user.first_name}-tx-{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}"

        url = "https://api.chapa.co/v1/transaction/initialize"
        current_site = Site.objects.get_current()
        relative_url = reverse('bookings')
        relative_url2 = reverse('chapa_webhook')
        redirect_url = f'https://{current_site.domain}{relative_url}'
        webhook_url = f'https://{current_site.domain}{relative_url2}'
        payload = {
            "amount": amount,
            "currency": "ETB",
            "email": self.booking.user.email,
            "first_name": self.booking.user.first_name,
            "last_name": self.booking.user.last_name,
            "phone_number": self.booking.user.phone_number,
            "redirect_url": redirect_url,
            "tx_ref": tx_ref,
            "callback_url": webhook_url,
        }
        headers = {
            'Authorization': 'Bearer CHASECK_TEST-h6dv4n5s2yutNrgiwTgWUpJKSma6Wsh9',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        print(data)
        if response.status_code == 200:
            Payment.objects.create(
                booking=self.booking,
                status='pending',
                transaction_id=tx_ref,
            )
            self.booking.status = 'confirmed'
            # self.booking.is_paid = True
            # self.booking.room.room_status = 'occupied'
            self.booking.save()
            checkout_url = data['data']['checkout_url']
            return redirect(checkout_url)
        else:
            return HttpResponse(response)
        
    def get_booking(self):
        booking_id = self.kwargs.get('booking_id')
        return get_object_or_404(Booking, id=booking_id)


from django.db import transaction

class BookingDeleteView(LoginRequiredMixin, DeleteView):
    model = Booking
    template_name = 'room/booking_confirm_delete.html'
    success_url = reverse_lazy('bookings')

    def get_queryset(self):
        owner_queryset = super().get_queryset()
        return owner_queryset.filter(user=self.request.user)

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        try:
            booking = self.get_object()
            room_id = booking.room.id
            response = super().delete(request, *args, **kwargs)
            room = Room.objects.get(id=room_id)
            room.update_room_status()  # Explicitly call update_room_status
            return response
        except Exception as e:
            print(f"Exception when deleting booking: {e}")
            return HttpResponseBadRequest("Error occurred while deleting the booking.")

from django.db.models import Q

class ReceiptUploadView(CreateView):
    model = Receipt
    fields = ['file']
    template_name = 'room/upload_receipt.html'

    def form_valid(self, form):
        booking = Booking.objects.get(id=self.kwargs['booking_id'])
        form.instance.booking = booking
        booking.is_paid = True
        booking.status = 'confirmed'
        booking.room.room_status = 'occupied'
        booking.room.save()
        booking.save()

        # Update the status of the payment to 'completed' if it exists
        Payment.objects.filter(Q(booking=booking) & Q(status='pending')).update(status='completed')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('bookings')

@method_decorator(csrf_exempt, name='dispatch')
class ChapaWebhookView(View):
    def post(self, request, *args, **kwargs):
        print(request.body)
        return HttpResponse('success')


from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Booking)
@receiver(post_delete, sender=Booking)
@receiver(post_save, sender=Reservation)
@receiver(post_delete, sender=Reservation)
def update_room_status(sender, instance, **kwargs):
    instance.room.update_room_status()

def update_room_statuses():
    now = timezone.now().date()
    rooms = Room.objects.all()
    for room in rooms:
        room.update_room_status()

# Call this function at the beginning of views that display room lists
