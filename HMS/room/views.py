from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Room, Booking, Payment, RoomRating,Receipt
from .forms import BookingForm, RoomRatingForm
import requests
import random
from django.db.models import Q
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
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
from django.core.mail import send_mail
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
from gym.models import *
import logging
from config import BASE_URL
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.http import HttpResponseNotFound
from django.http import HttpResponseServerError
from django.core.mail import EmailMultiAlternatives
from premailer import transform
from Hall.models import *



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

    def cancel_past_bookings(self):
        past_bookings = Booking.objects.filter(
                        Q(check_out_date__lt=timezone.now().date()) | Q(extended_check_out_date__lt=timezone.now().date()),
                        user=self.request.user).exclude(status='cancelled')
        for booking in past_bookings:
            booking.status = 'cancelled'
            booking.save()
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




class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'room/bookings.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        self.cancel_past_bookings() 
        return Booking.objects.filter(user=self.request.user).exclude(status__in=['cancelled'])
    def cancel_past_bookings(self):
        past_bookings = Booking.objects.filter(
                        Q(check_out_date__lt=timezone.now().date()) | Q(extended_check_out_date__lt=timezone.now().date()),
                        user=self.request.user).exclude(status='cancelled')
        for booking in past_bookings:
            booking.status = 'cancelled'
            booking.save()




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
        context['room_type'] = room.room_type
        context['price_per_night'] = room.price_per_night  
        return context

    def form_valid(self, form):
        room = get_object_or_404(Room, id=self.kwargs['room_id'])
        form.instance.user = self.request.user
        form.instance.room = room
        form.instance.status = 'pending'
        form.instance.tx_ref = f"booking-{self.request.user.first_name}-tx-{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}"

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
            if booking.extended_check_out_date == booking.check_out_date:
                messages.warning(request, 'Payment Already Completed')
                return redirect('bookings')
            booking.booking_extend_amount = booking.calculate_additional_amount()
            booking.save()
            amount = booking.booking_extend_amount
            tx_ref = f"booking-{self.request.user.first_name}-tx-{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}"
            booking.tx_ref = tx_ref
            booking.save()

            if payment_method == 'chapa':
                amount=str(amount)
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
        redirect_url = f"{BASE_URL}"
        webhook_url = f"{BASE_URL}/room/chapa-webhook/"
        print(webhook_url)

        payload = {
            "amount": str(amount),
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
        paypalrestsdk.configure({
            "mode": "sandbox",  # sandbox or live
            "client_id": "ARbeUWx-il1YsBMeVLQpy2nFI4l3vsuwipJXyhWo1Bmee4YYyuxQWrzX7joSU0IZfytEJ4s3rteXh5kj",
            "client_secret": "EFph5hrjs9Pok_vmU3JbkY2RVZ0FA8HlG-uhkEytPrxn6k1YwWz6_t4ph03eesiYTFhsYsgJgyRYkLuF"
        })
        amount_in_dollars = amount/50
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"},
            "redirect_urls": {
                "return_url": f"{BASE_URL}/room/paypal-return/?booking_id={booking.id}",
                "cancel_url": f"{BASE_URL}/room/paypal-cancel/?booking_id={booking.id}"},
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "room booking",
                        "sku": "item",
                        "price": str(amount_in_dollars),
                        "currency": "USD",
                        "quantity": 1}]},
                "amount": {
                    "total": str(amount_in_dollars),
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
        context['amount'] = self.booking.original_booking_amount
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
            return redirect('bookings')
        amount = str(self.booking.original_booking_amount)
        tx_ref = f"booking-{self.request.user.first_name}-tx-{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}"
        self.booking.tx_ref = tx_ref  # Store the new tx_ref in booking
        self.booking.save()

        url = "https://api.chapa.co/v1/transaction/initialize"
        redirect_url = f"{BASE_URL}"
        webhook_url = f"{BASE_URL}/room/chapa-webhook/"
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
        amount_in_dollars= self.booking.original_booking_amount/50
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"},
            "redirect_urls": {
                "return_url": f"{BASE_URL}/room/paypal-return/?booking_id={self.booking.id}",
                "cancel_url": f"{BASE_URL}/room/paypal-cancel/?booking_id={self.booking.id}"},
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "room booking",
                        "sku": "item",
                        "price": str(amount_in_dollars),
                        "currency": "USD",
                        "quantity": 1}]},
                "amount": {
                    "total": str(amount_in_dollars),
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
                booking.tx_ref = f"booking-{self.request.user.first_name}-tx-{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}"
                # booking.room.status='occupied'
                # Check if booking.total_amount is None and use 0 if it is, otherwise use its value
                if booking.booking_extend_amount is None:
                    booking.total_amount = booking.original_booking_amount
                booking.save()
                if booking.extended_check_out_date:
                    booking.check_out_date=booking.extended_check_out_date
                    if booking.booking_extend_amount is not None:
                        booking.total_amount += booking.booking_extend_amount 
                    booking.save(bypass_validation=True)
                payment, created = Payment.objects.get_or_create(
                            booking=booking,
                            defaults={
                                'status': 'completed',
                                'transaction_id': booking.tx_ref,
                                'payment_method': 'paypal'
                                }
                                )
                messages.success(request, 'Payment completed successfully.')
                
                booking_url = f"{BASE_URL}/room/my-bookings/"
                if booking.extended_check_out_date:
                    subject = 'Room Booking Extension Confirmation'
                    html_content = render_to_string('room/checkout_date_extenstion_email_template.html', {'booking': booking, 'booking_url': booking_url})
                else:
                    subject = 'Room Booking Confirmation'
                    html_content = render_to_string('room/booking_confirmation_template.html', {'booking': booking, 'booking_url': booking_url})
                # Inline CSS
                html_content = transform(html_content)

                # Create the email message
                email = EmailMultiAlternatives(
                    subject=subject,
                    from_email='adarhotel33@gmail.com',
                    to=[booking.user.email]
                )
                # Attach the HTML content
                email.attach_alternative(html_content, "text/html")

                # Send the email
                email.send()
                
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

        if tx_ref.startswith('booking'):
            return self.process_booking_payment(tx_ref, payload)
        elif tx_ref.startswith('hall_booking'):
            return self.process_hall_booking_payment(tx_ref, payload)
        elif tx_ref.startswith('membership'):
            return self.process_membership_payment(tx_ref, payload)
        else:
            print("Invalid tx_ref prefix")
            return HttpResponseBadRequest("Invalid tx_ref prefix")

    def process_booking_payment(self, tx_ref, payload):
        try:
            booking = Booking.objects.get(tx_ref=tx_ref)
        except Booking.DoesNotExist:
            print("Booking not found")
            return HttpResponseNotFound("Booking not found")
        except Booking.MultipleObjectsReturned:
            print("Multiple bookings found")
            return HttpResponseServerError("Multiple bookings found")

        print("Booking found:", booking)

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
            payment.status = 'completed'
            payment.transaction_id = tx_ref
            payment.save()

        print("Payment record created or updated:", payment)

        booking.is_paid = True
        booking.status = 'confirmed'
        booking.room.room_status = 'occupied'
        booking.room.save()
        booking.save()
        print('hh', booking.booking_extend_amount)
        if booking.booking_extend_amount is None:
            booking.total_amount = booking.original_booking_amount
            print("", booking.total_amount)
            booking.save()
        if booking.extended_check_out_date:
            booking.check_out_date = booking.extended_check_out_date
            if booking.booking_extend_amount is not None:
                print("", booking.total_amount)
                print("", booking.booking_extend_amount)
                booking.total_amount += booking.booking_extend_amount
            booking.save(bypass_validation=True)

        
        booking_url = f"{BASE_URL}/room/my-bookings/"
        if booking.extended_check_out_date:
            subject = 'Room Booking Extension Confirmation'
            html_content = render_to_string('room/checkout_date_extenstion_email_template.html', {'booking': booking, 'booking_url': booking_url})
        else:
            subject = 'Room Booking Confirmation'
            html_content = render_to_string('room/booking_confirmation_template.html', {'booking': booking, 'booking_url': booking_url})
        # Inline CSS
        html_content = transform(html_content)

        # Create the email message
        email = EmailMultiAlternatives(
            subject=subject,
            from_email='adarhotel33@gmail.com',
            to=[booking.user.email]
        )
        # Attach the HTML content
        email.attach_alternative(html_content, "text/html")

        # Send the email
        email.send()
            
        print("Booking and room updated")
        return HttpResponse("Booking webhook processed successfully")

    def process_hall_booking_payment(self, tx_ref, payload):
        try:
            booking = Hall_Booking.objects.get(tx_ref=tx_ref)
        except Hall_Booking.DoesNotExist:
            print("Hall Booking not found")
            return HttpResponseNotFound("Hall Booking not found")
        except Hall_Booking.MultipleObjectsReturned:
            print("Multiple hall bookings found")
            return HttpResponseServerError("Multiple hall bookings found")

        print("Hall Booking found:", booking)

        payment, created = Hall_Payment.objects.get_or_create(
            booking=booking,
            defaults={
                'status': 'completed',
                'transaction_id': tx_ref,
                'payment_method': 'chapa'
            }
        )

        if not created:
            print("Payment already exists for this booking.")
            payment.status = 'completed'
            payment.transaction_id = tx_ref
            payment.save()

        print("Payment record created or updated:", payment)

        
        booking.status = 'confirmed'
        booking.is_paid = True
        booking.save()

        booking_url = f"{BASE_URL}/hall/my-bookings/"
        html_content = render_to_string('hall/booking_confirmation_template.html', {'booking': booking, 'booking_url': booking_url})

        
        # Create the email message with only HTML content
        email = EmailMultiAlternatives(
            subject='Hall Booking Confirmation',
            from_email='adarhotel33@gmail.com',
            to=[booking.user.email]
        )
        # Attach the HTML content
        email.attach_alternative(html_content, "text/html")

        # Send the email
        email.send()

        print("Hall booking updated")
        return HttpResponse("Hall booking webhook processed successfully")
   
    def process_membership_payment(self, tx_ref, payload):
        try:
            membership = Membership.objects.get(tx_ref=tx_ref)
        except Membership.DoesNotExist:
            print("Membership not found")
            return HttpResponseNotFound("Membership not found")
        except Membership.MultipleObjectsReturned:
            print("Multiple memberships found")
            return HttpResponseServerError("Multiple memberships found")

        print("Membership found:", membership)

        membership_payment, created = MembershipPayment.objects.get_or_create(
            membership=membership,
            defaults={
                'status': 'completed',
                'transaction_id': tx_ref,
                'amount': payload.get('amount'),
                'payment_method' : 'chapa'
            }
        )

        if not created:
            print("Payment already exists for this membership.")
            membership_payment.status = 'completed'
            membership_payment.transaction_id = tx_ref
            membership_payment.payment_method ='chapa'
            membership_payment.save()

        print("Payment record created or updated:", membership_payment)

        membership.status = 'active'
        membership.save()
        membership_url = f"{BASE_URL}/gym/my-memberships/"
        html_content = render_to_string('gym/membership_confirmation_template.html', {'membership': membership, 'membership_url': membership_url})

        
        # Create the email message with only HTML content
        email = EmailMultiAlternatives(
            subject='Gym Membership Confirmation',
            from_email='adarhotel33@gmail.com',
            to=[membership.user.email]
        )
        # Attach the HTML content
        email.attach_alternative(html_content, "text/html")

        # Send the email
        email.send()
        print("Membership updated")

        return HttpResponse("Membership webhook processed successfully")


        

logger = logging.getLogger(__name__)



class BookingCancelView(LoginRequiredMixin, UpdateView):
    model = Booking
    fields = []  # No fields to update through the form
    success_url = reverse_lazy('bookings')

    def get_queryset(self):
        owner_queryset = super().get_queryset()
        return owner_queryset.filter(user=self.request.user)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            booking = self.get_object()
            booking.status = 'cancelled'
            booking.save(bypass_validation=True)
            booking.room.update_room_status()
            # Update the room status after cancellation
            booking_url = f"{BASE_URL}/room/my-bookings/"
            html_content = render_to_string('room/cancellation_email_template.html', {'booking': booking, 'booking_url': booking_url})
            
            # Inline CSS
            html_content = transform(html_content)
            
            # Create the email message with only HTML content
            email = EmailMultiAlternatives(
                subject='Booking Cancellation Confirmation',
                from_email='adarhotel33@gmail.com',
                to=[booking.user.email]
            )
            # Attach the HTML content
            email.attach_alternative(html_content, "text/html")
            
            # Send the email
            email.send()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            print(f"Exception when canceling booking: {e}")
            return HttpResponseBadRequest("Error occurred while canceling the booking.")


    def form_invalid(self, form):
        return HttpResponseRedirect(self.success_url)




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
def update_room_status(sender, instance, **kwargs):
    instance.room.update_room_status()

def update_room_statuses():
    now = timezone.now().date()
    rooms = Room.objects.all()
    for room in rooms:
        room.update_room_status()
