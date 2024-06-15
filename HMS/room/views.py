from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Room, Booking, Reservation, Payment, RoomRating,Receipt
from .forms import BookingForm, ReservationForm, RoomRatingForm
import requests
import random
from django.db.models import Min, Max
from django.http import JsonResponse
from django.http import HttpResponseRedirect
import string
from paypalrestsdk import Payment as PayPalPayment
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.dispatch import receiver
import requests
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic.edit import FormView
from .models import *
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
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from .forms import BookingExtendForm
from .models import Booking
from datetime import timedelta, date
from django.db import transaction
from django.db.models import Q
import json
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.http import HttpResponseNotFound
from django.http import HttpResponseServerError



def home(request):
    rooms = Room.objects.available().filter(room_status='vacant').order_by('room_type', 'id').distinct('room_type')
    print(rooms)
    return render(request, 'room/home.html', {'rooms': rooms})

class RoomListView(ListView):
    model = Room
    template_name = 'room/rooms.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        queryset = Room.objects.available().filter(room_status='vacant')
        price = self.request.GET.get('price')
        room_type = self.request.GET.get('room_type')
        
        if price:
            queryset = queryset.filter(price_per_night__lte=price)
        if room_type:
            queryset = queryset.filter(room_type__id=room_type)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        context['room_types'] = Category.objects.all()  # Assuming Category is your room type model

        min_price = Room.objects.aggregate(Min('price_per_night'))['price_per_night__min']
        max_price = Room.objects.aggregate(Max('price_per_night'))['price_per_night__max']

        if min_price is not None and max_price is not None:
            context['price_range'] = range(int(min_price), int(max_price) + 1, 100)  # Adjust the step as needed
        else:
            context['price_range'] = []

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
        return Booking.objects.filter(user=self.request.user).exclude(status__in=['cancelled'])


from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from .models import Room, Booking
from .forms import BookingForm

class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'room/booking_create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['room'] = get_object_or_404(Room, id=self.kwargs['room_id'])
        return kwargs

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
        form.instance.tx_ref = f"{self.request.user.first_name}-tx-{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}"
        self.object = form.save()
        return redirect('payment_create', booking_id=self.object.id)

    def form_invalid(self, form):
        print("Form is invalid")
        print(form.errors)  # Print form errors to the console for debugging
        return self.render_to_response(self.get_context_data(form=form))




from .forms import BookingExtendForm

class BookingExtendView(View):
    template_name = 'room/booking_extend.html'

    def get(self, request, *args, **kwargs):
        booking = self.get_booking()
        form = BookingExtendForm(instance=booking)
        context = self.get_context_data(booking, form)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        booking = self.get_booking()
        form = BookingExtendForm(request.POST, instance=booking)

        if form.is_valid():
            extended_check_out_date = form.cleaned_data['extended_check_out_date']
            if extended_check_out_date <= booking.check_out_date:
                form.add_error('extended_check_out_date', 'Extended check-out date must be after the current check-out date.')
                return self.form_invalid(form)
            elif extended_check_out_date <= booking.check_in_date:
                form.add_error('extended_check_out_date', 'Extended check-out date cannot be before the current check-in date.')
                return self.form_invalid(form)
            else:
                booking.extended_check_out_date = extended_check_out_date
                booking.status = 'pending'
                booking.save()
                return redirect('payment_extend', booking_id=booking.id)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        booking = self.get_booking()
        return render(self.request, self.template_name, self.get_context_data(booking=booking, form=form))

    def get_booking(self):
        booking_id = self.kwargs.get('booking_id')
        return get_object_or_404(Booking, id=booking_id)

    def get_context_data(self, booking, form):
        context = {
            'booking': booking,
            'form': form
        }
        return context

    



class PaymentExtendView(View):
    template_name = 'room/payment_extend.html'

    def get(self, request, *args, **kwargs):
        booking = self.get_booking()
        context = self.get_context_data(booking)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        booking = self.get_booking()
        payment_method = request.POST.get('payment_method')
        
        if booking.is_paid or booking.status != 'confirmed':
            booking.status = 'pending'
            booking.save()
            amount = str(booking.calculate_additional_amount())
            tx_ref = f"{booking.user.first_name}-tx-{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}"
            booking.tx_ref = tx_ref
            booking.save()

            if payment_method == 'chapa':
                return self.process_chapa_payment(booking, amount, tx_ref)
            elif payment_method == 'paypal':
                return self.process_paypal_payment(booking, amount)
            else:
                messages.error(request, 'Invalid payment method selected.')
                return render(request, self.template_name, self.get_context_data(booking=booking))
        else:
            messages.warning(request, 'Booking cannot be extended.')
            return redirect('bookings')

    def get_booking(self):
        booking_id = self.kwargs.get('booking_id')
        return get_object_or_404(Booking, id=booking_id)

    def get_context_data(self, booking):
        context = {
            'booking': booking,
            'amount': booking.calculate_additional_amount()
        }
        return context

    def process_chapa_payment(self, booking, amount, tx_ref):
        url = "https://api.chapa.co/v1/transaction/initialize"
        current_site = Site.objects.get_current()
        relative_url = reverse('bookings')
        redirect_url = f'https://{current_site.domain}{relative_url}'
        webhook_url = 'https://4302-102-218-50-52.ngrok-free.app/room/chapa-webhook/'

        payload = {
            "amount": amount,
            "currency": "ETB",
            "email": booking.user.email,
            "first_name": booking.user.first_name,
            "last_name": booking.user.last_name,
            "phone_number": booking.user.phone_number,
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
        if response.status_code == 200:
            checkout_url = data['data']['checkout_url']
            return redirect(checkout_url)
        else:
            return HttpResponse(response)

    def process_paypal_payment(self, booking, amount):
        if booking.is_paid or booking.status != 'pending':
            messages.warning(self.request, 'Payment already completed')
            return render(self.request, self.template_name, self.get_context_data(booking=booking))
        
        paypalrestsdk.configure({
            "mode": "sandbox",  # sandbox or live
            "client_id": "ARbeUWx-il1YsBMeVLQpy2nFI4l3vsuwipJXyhWo1Bmee4YYyuxQWrzX7joSU0IZfytEJ4s3rteXh5kj",
            "client_secret": "EFph5hrjs9Pok_vmU3JbkY2RVZ0FA8HlG-uhkEytPrxn6k1YwWz6_t4ph03eesiYTFhsYsgJgyRYkLuF"
        })

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"},
            "redirect_urls": {
                "return_url": f"https://4302-102-218-50-52.ngrok-free.app/room/paypal-return/?booking_id={booking.id}",
                "cancel_url": f"https://4302-102-218-50-52.ngrok-free.app/room/paypal-cancel/?booking_id={booking.id}"},
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "room booking",
                        "sku": "item",
                        "price": amount,
                        "currency": "USD",
                        "quantity": 1}]},
                "amount": {
                    "total": amount,
                    "currency": "USD"},
                "description": "This is the payment transaction description."}]})

        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    break
            else:
                return HttpResponse("No approval URL returned by PayPal")
            return HttpResponseRedirect(approval_url)
        else:
            return HttpResponse("Error: " + payment.error)



# Set up logging
logger = logging.getLogger(__name__)
import paypalrestsdk

from django.http import JsonResponse
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
        payment_method = request.POST.get('payment_method')
        if payment_method == 'chapa':
            return self.process_chapa_payment()
        elif payment_method == 'paypal':
            return self.process_paypal_payment()
        else:
            messages.error(request, 'Invalid payment method selected.')
            return render(request, self.template_name, self.get_context_data())

    def get_booking(self):
        booking_id = self.kwargs.get('booking_id')
        return get_object_or_404(Booking, id=booking_id)
    
    def process_chapa_payment(self):
        if self.booking.is_paid or self.booking.status != 'pending':
            messages.warning(self.request, 'Payment already completed')
            return render(self.request, self.template_name, self.get_context_data())
        amount = str(self.booking.total_amount)
        tx_ref = f"{self.booking.user.first_name}-tx-{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}"
        self.booking.tx_ref = tx_ref  # Store the new tx_ref in booking
        self.booking.save()

        url = "https://api.chapa.co/v1/transaction/initialize"
        redirect_url = f'https://4302-102-218-50-52.ngrok-free.app/room/bookings'
        webhook_url = f'https://4302-102-218-50-52.ngrok-free.app/room/chapa-webhook/'
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
        if response.status_code == 200:
            checkout_url = data['data']['checkout_url']
            return redirect(checkout_url)
        else:
            return HttpResponse(response)
    

    def process_paypal_payment(self):
        if self.booking.is_paid or self.booking.status != 'pending':
            messages.warning(self.request, 'Payment already completed')
            return render(self.request, self.template_name, self.get_context_data())
        paypalrestsdk.configure({
            "mode": "sandbox",  # sandbox or live
            "client_id": "ARbeUWx-il1YsBMeVLQpy2nFI4l3vsuwipJXyhWo1Bmee4YYyuxQWrzX7joSU0IZfytEJ4s3rteXh5kj",
            "client_secret": "EFph5hrjs9Pok_vmU3JbkY2RVZ0FA8HlG-uhkEytPrxn6k1YwWz6_t4ph03eesiYTFhsYsgJgyRYkLuF"
        })

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"},
            "redirect_urls": {
                "return_url": f"http://4302-102-218-50-52.ngrok-free.app/room/paypal-return/?booking_id={self.booking.id}",
                "cancel_url": f"http://4302-102-218-50-52.ngrok-free.app/room/paypal-cancel/?booking_id={self.booking.id}"},
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "room booking",
                        "sku": "item",
                        "price": str(self.booking.total_amount),
                        "currency": "USD",
                        "quantity": 1}]},
                "amount": {
                    "total": str(self.booking.total_amount),
                    "currency": "USD"},
                "description": "This is the payment transaction description."}]})

        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    break
            else:
                return HttpResponse("No approval URL returned by PayPal")
            return HttpResponseRedirect(approval_url)
        else:
            return HttpResponse("Error: " + payment.error)
    
    





class PayPalReturnView(View):
    def get(self, request, *args, **kwargs):
        payment_id = request.GET.get('paymentId')
        payer_id = request.GET.get('PayerID')
        booking_id = request.GET.get('booking_id')
        booking = get_object_or_404(Booking, id=booking_id)

        # Execute the payment
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            if payment.state == "approved":
                booking.is_paid = True
                booking.status = 'confirmed'
                # booking.room.status='occupied'
                booking.save()
                payment, created = Payment.objects.get_or_create(
                            booking=booking,
                            defaults={
                                'status': 'completed',
                                'transaction_id': booking.tx_ref,
                                'payment_method': 'paypal'
                                }
                                )
                messages.success(request, 'Payment completed successfully.')
                return redirect('bookings')
            else:
                messages.error(request, 'Payment was not successful.')
                return redirect('payment_create', booking_id=booking.id)
        else:
            messages.error(request, 'There was an issue with your PayPal payment.')
            return redirect('payment_create', booking_id=booking.id)

class PayPalCancelView(View):
    def get(self, request, *args, **kwargs):
        booking_id = request.GET.get('booking_id')
        messages.warning(request, 'Payment was cancelled.')
        return redirect('payment_page', booking_id=booking_id)



@method_decorator(csrf_exempt, name='dispatch')
class ChapaWebhookView(View):
    def post(self, request, *args, **kwargs):
        print("Webhook received")
        payload = json.loads(request.body)
        print("Payload:", payload)
        
        tx_ref = payload.get('tx_ref')
        print("Transaction reference:", tx_ref)

        if not tx_ref:
            print("Invalid tx_ref")
            return HttpResponseBadRequest("Invalid tx_ref")

        try:
            booking = Booking.objects.get(tx_ref=tx_ref)
        except Booking.DoesNotExist:
            print("Booking not found")
            return HttpResponseNotFound("Booking not found")
        except Booking.MultipleObjectsReturned:
            print("Multiple bookings found")
            return HttpResponseServerError("Multiple bookings found")

        print("Booking found:", booking)

        # Check if a payment already exists for this booking
        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={
                'status': 'completed',
                'transaction_id': tx_ref,
                'payment_method': 'chapa'
            }
        )

        if not created:
            print("Payment already exists for this booking.")
            # Update payment status if necessary
            payment.status = 'completed'
            payment.transaction_id = tx_ref
            payment.save()

        print("Payment record created or updated:", payment)

        # Update booking and room status
        booking.is_paid = True
        booking.status = 'confirmed'
        if booking.extended_check_out_date:
            print(booking.check_out_date)
            print(booking.extended_check_out_date)
            print(booking.check_out_date)
        booking.room.room_status = 'occupied'
        booking.room.save()
        booking.save()
        print("Booking and room updated")

        return HttpResponse("Webhook processed successfully")


        





class BookingCancelView(LoginRequiredMixin, UpdateView):
    model = Booking
    fields = []  # No fields to update through the form
    template_name = 'room/booking_confirm_cancel.html'
    success_url = reverse_lazy('bookings')

    def get_queryset(self):
        owner_queryset = super().get_queryset()
        return owner_queryset.filter(user=self.request.user)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            booking = self.get_object()
            booking.status = 'cancelled'
            booking.save()
            booking.room.update_room_status()  # Update the room status after cancellation
            return super().post(request, *args, **kwargs)
        except Exception as e:
            print(f"Exception when canceling booking: {e}")
            return HttpResponseBadRequest("Error occurred while canceling the booking.")

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




class ReceiptUploadView(CreateView):
    model = Receipt
    fields = ['file']
    template_name = 'room/upload_receipt.html'

    def form_valid(self, form):
        booking = Booking.objects.get(id=self.kwargs['booking_id'])
        form.instance.booking = booking

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('bookings')




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
