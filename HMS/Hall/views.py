# views.py
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .models import Hall, Hall_Booking
from django.views.generic import DetailView, FormView
from .models import Hall, Hall_Booking, Hall_Payment,Hall_Category
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from .forms import CheckAvailabilityForm, BookingForm
import datetime
import random
import string
import requests
from decimal import Decimal
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from premailer import transform
import paypalrestsdk
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.db import transaction
import json
from config import BASE_URL
from django.utils import timezone
from django.db.models import Min, Max

class HallListView(ListView):
    model = Hall
    template_name = 'hall/hall_list.html'
    context_object_name = 'halls'

    def get_queryset(self):
        queryset = Hall.objects.filter(status='available')  # Adjust the status field as per your model
        price = self.request.GET.get('price')
        hall_type = self.request.GET.get('hall_type')

        if price:
            queryset = queryset.filter(price_per_hour__lte=price)
        if hall_type:
            queryset = queryset.filter(hall_type__id=hall_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        context['hall_types'] = Hall_Category.objects.all()  # Assuming HallType is your hall type model

        min_price = Hall.objects.aggregate(Min('price_per_hour'))['price_per_hour__min']
        max_price = Hall.objects.aggregate(Max('price_per_hour'))['price_per_hour__max']

        if min_price is not None and max_price is not None:
            context['price_range'] = range(int(min_price), int(max_price) + 1, 100)  # Adjust the step as needed
        else:
            context['price_range'] = []

        return context
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
            'start_time':  datetime.datetime.strptime(start_time, '%H:%M:%S').time(),
            'end_time':  datetime.datetime.strptime(end_time, '%H:%M:%S').time(),
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
            status='pending'
        )

        # Clear booking data from session
        del request.session['booking_data']
         

        return redirect('payment_page', pk=booking.pk)



    


class PaymentView(TemplateView):
    template_name = 'hall/payment_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = get_object_or_404(Hall_Booking, pk=self.kwargs['pk'])
        context['booking'] = booking
        return context

    def post(self, request, *args, **kwargs):
        booking = get_object_or_404(Hall_Booking, pk=self.kwargs['pk'])
        payment_method = request.POST.get('payment_method')

        if payment_method == 'chapa':
            return self.process_chapa_payment(booking)
        elif payment_method == 'paypal':
            return self.process_paypal_payment(booking)
        else:
            messages.error(request, 'Invalid payment method selected.')
            return render(request, self.template_name, self.get_context_data())

    def process_chapa_payment(self, booking):
        if booking.is_paid or booking.status != 'pending':
            messages.warning(self.request, 'Payment already completed')
            return redirect('hall_bookings')

        amount = str(booking.amount_due)
        tx_ref = f"hall_booking-{self.request.user.first_name}-tx-{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}"
        booking.tx_ref = tx_ref  # Store the new tx_ref in booking
        booking.save()

        url = "https://api.chapa.co/v1/transaction/initialize"
        redirect_url = f"{BASE_URL}/hall/chapa-return/"
        webhook_url = f"{BASE_URL}/hall/chapa-webhook/"
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

    def process_paypal_payment(self, booking):
        if booking.status != 'pending':
            messages.warning(self.request, 'Payment already completed')
            return render(self.request, self.template_name, self.get_context_data())

        paypalrestsdk.configure({
            "mode": "sandbox",  # sandbox or live
            "client_id": "ARbeUWx-il1YsBMeVLQpy2nFI4l3vsuwipJXyhWo1Bmee4YYyuxQWrzX7joSU0IZfytEJ4s3rteXh5kj",
            "client_secret": "EFph5hrjs9Pok_vmU3JbkY2RVZ0FA8HlG-uhkEytPrxn6k1YwWz6_t4ph03eesiYTFhsYsgJgyRYkLuF"
        })
        amount_in_dollars = booking.amount_due / 50
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": f"{BASE_URL}/hall/paypal-return/?booking_id={booking.id}",
                "cancel_url": f"{BASE_URL}/hall/paypal-cancel/?booking_id={booking.id}"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "hall booking",
                        "sku": "item",
                        "price": str(amount_in_dollars),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(amount_in_dollars),
                    "currency": "USD"
                },
                "description": "This is the payment for booking hall."
            }]
        })

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
        booking = get_object_or_404(Hall_Booking, id=booking_id)

        # Execute the payment
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            if payment.state == "approved":
                booking.status = 'confirmed'
                booking.is_paid = True
                booking.tx_ref = f"hall_booking-{self.request.user.first_name}-tx-{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}"
                booking.save()

                payment_record, created = Hall_Payment.objects.get_or_create(
                    booking=booking,
                    defaults={
                        'status': 'completed',
                        'transaction_id': booking.tx_ref,
                        'payment_method': 'paypal'
                    }
                )

                messages.success(request, 'Payment completed successfully.')
                # booking_url = f"{settings.BASE_URL}/hall/my-bookings/"
                # subject = 'Hall Booking Confirmation'
                # html_content = render_to_string('hall/booking_confirmation_template.html', {'booking': booking, 'booking_url': booking_url})
                # html_content = transform(html_content)

                # email = EmailMultiAlternatives(
                #     subject=subject,
                #     from_email='your_email@example.com',
                #     to=[booking.user.email]
                # )
                # email.attach_alternative(html_content, "text/html")
                # email.send()

                return redirect('hall_bookings')
            else:
                messages.error(request, 'Payment was not successful.')
                return redirect('payment_page', booking_id=booking.id)
        else:
            messages.error(request, 'There was an issue with your PayPal payment.')
            return redirect('payment_page', booking_id=booking.id)

class PayPalCancelView(View):
    def get(self, request, *args, **kwargs):
        booking_id = request.GET.get('booking_id')
        messages.warning(request, 'Payment was cancelled.')
        return redirect('payment_page', booking_id=booking_id)


class BookingListView(ListView):
    model = Hall_Booking
    template_name = 'hall/my_bookings.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return Hall_Booking.objects.filter(user=self.request.user).exclude(status='cancelled')



class HallBookingCancelView(LoginRequiredMixin, UpdateView):
    model = Hall_Booking
    fields = []  # No fields to update through the form
    success_url = reverse_lazy('hall_bookings')  # Replace with your actual URL name for the hall bookings list

    def get_queryset(self):
        owner_queryset = super().get_queryset()
        return owner_queryset.filter(user=self.request.user)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            booking = self.get_object()
            booking.status = 'cancelled'
            booking.save()

            
            # # Prepare the booking URL and render the cancellation email template
            # booking_url = f"{BASE_URL}/hall/my-bookings/"
            # html_content = render_to_string('hall/cancellation_email_template.html', {'booking': booking, 'booking_url': booking_url})

            # # Inline CSS using WeasyPrint (if required)
            # html_content = HTML(string=html_content).write_pdf()

            # # Create the email message with only HTML content
            # email = EmailMultiAlternatives(
            #     subject='Hall Booking Cancellation Confirmation',
            #     from_email='adarhotel33@gmail.com',
            #     to=[booking.user.email]
            # )
            # # Attach the HTML content
            # email.attach_alternative(html_content, "text/html")

            # # Send the email
            # email.send()

            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            print(f"Exception when canceling hall booking: {e}")
            return HttpResponseBadRequest("Error occurred while canceling the hall booking.")

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        try:
            booking = self.get_object()
            hall_id = booking.hall.id
            response = super().delete(request, *args, **kwargs)
            hall = Hall.objects.get(id=hall_id)
            return response
        except Exception as e:
            print(f"Exception when deleting hall booking: {e}")
            return HttpResponseBadRequest("Error occurred while deleting the hall booking.")

    def form_invalid(self, form):
        return HttpResponseRedirect(self.success_url)
