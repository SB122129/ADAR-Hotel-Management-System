from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from paypalrestsdk import Payment, configure
from django.views.generic import ListView, FormView, View
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import MembershipPlan, Membership, MembershipPayment
from .forms import MembershipSignupForm
from dateutil.relativedelta import relativedelta
import random
import string
import requests
import paypalrestsdk



class MyMembershipsView(LoginRequiredMixin, ListView):
    model = Membership
    template_name = 'gym/my_memberships.html'
    context_object_name = 'memberships'

    def get_queryset(self):
        return Membership.objects.filter(user=self.request.user)


class MembershipPlanListView(LoginRequiredMixin, ListView):
    model = MembershipPlan
    template_name = 'gym/membership_plans.html'
    context_object_name = 'plans'

    def get_queryset(self):
        return MembershipPlan.objects.all().order_by('price')


class MembershipSignupView(LoginRequiredMixin, FormView):
    form_class = MembershipSignupForm
    template_name = 'gym/membership_signup.html'

    def get_initial(self):
        initial = super().get_initial()
        plan_id = self.kwargs['plan_id']
        start_date = self.request.GET.get('start_date')
        initial['plan_id'] = plan_id
        initial['start_date'] = start_date
        return initial

    def form_valid(self, form):
        plan_id = self.kwargs['plan_id']
        plan = get_object_or_404(MembershipPlan, id=plan_id)
        user = self.request.user
        start_date_str = self.request.GET.get('start_date')
        existing_membership_id = self.request.GET.get('membership_id', None)
        subscription_for = self.request.GET.get('subscription_for', 'self')
        first_name = self.request.GET.get('first_name')
        last_name = self.request.GET.get('last_name')
        phone_number = self.request.GET.get('phone_number')
        email = self.request.GET.get('email')

        # Parse start_date from string to date
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(self.request, 'Invalid start date format.')
            return redirect('my_memberships')

        if existing_membership_id:
            try:
                membership = Membership.objects.get(
                    id=existing_membership_id, 
                    user=user, 
                    plan=plan, 
                    start_date=start_date, 
                    status='pending'
                )
            except Membership.DoesNotExist:
                return self.handle_no_membership_found(self.request)
        else:
            # Check for existing similar membership with status 'active' or 'pending'
            existing_membership = Membership.objects.filter(
                user=user,
                plan=plan,
                start_date=start_date,
                status__in=['active', 'pending']
            ).exists()

            if existing_membership:
                messages.error(self.request, 'A similar membership already exists.')
                return redirect('my_memberships')

            # Generate a tx_ref and check if it already exists
            tx_ref = f"membership-{self.request.user.first_name}-tx-{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}"
            if Membership.objects.filter(tx_ref=tx_ref, status='pending').exists():
                messages.error(self.request, 'A similar membership transaction is already in progress.')
                return redirect('my_memberships')

            # Create a new membership entry with pending status
            membership = Membership.objects.create(
                user=user,
                plan=plan,
                start_date=start_date,
                end_date=start_date + relativedelta(months=plan.duration_months),
                status='pending',
                tx_ref=tx_ref,
                for_first_name=first_name if subscription_for == 'others' else user.first_name,
                for_last_name=last_name if subscription_for == 'others' else user.last_name,
                for_phone_number=phone_number if subscription_for == 'others' else user.phone_number
                for_email=email if subscription_for == 'others' else user.email                   
            )

        payment_method = form.cleaned_data['payment_method']

        # Initiate payment based on the selected payment method
        if payment_method == 'chapa':
            return self.initiate_chapa_payment(membership)
        elif payment_method == 'paypal':
            return self.initiate_paypal_payment(membership, plan_id)
        else:
            messages.error(self.request, 'Invalid payment method selected.')
            return redirect('membership_plans')

    def initiate_chapa_payment(self, membership):
        amount = str(membership.plan.price)
        tx_ref = membership.tx_ref
        membership.save()

        url = "https://api.chapa.co/v1/transaction/initialize"
        redirect_url = f'https://broadly-lenient-adder.ngrok-free.app/gym/bookings'
        webhook_url = f'https://broadly-lenient-adder.ngrok-free.app/room/chapa-webhook/'

        payload = {
            "amount": amount,
            "currency": "ETB",
            "email": self.request.user.email,
            "first_name": self.request.user.first_name,
            "last_name": self.request.user.last_name,
            "phone_number": self.request.user.phone_number,
            "redirect_url": self.request.build_absolute_uri(redirect_url),
            "tx_ref": tx_ref,
            "callback_url": webhook_url,
        }
        headers = {
            'Authorization': 'Bearer CHASECK_TEST-h6dv4n5s2yutNrgiwTgWUpJKSma6Wsh9',
            'Content-Type': 'application/json'
        }

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if response.status_code == 200 and data['status'] == 'success':
            return redirect(data['data']['checkout_url'])
        else:
            messages.error(self.request, 'Error initializing Chapa payment.')
            return redirect('membership_plans')

    def initiate_paypal_payment(self, membership, plan_id):
        configure({
            "mode": "sandbox",  # sandbox or live
            "client_id": "ARbeUWx-il1YsBMeVLQpy2nFI4l3vsuwipJXyhWo1Bmee4YYyuxQWrzX7joSU0IZfytEJ4s3rteXh5kj",
            "client_secret": "EFph5hrjs9Pok_vmU3JbkY2RVZ0FA8HlG-uhkEytPrxn6k1YwWz6_t4ph03eesiYTFhsYsgJgyRYkLuF"
        })

        payment = Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": f"https://broadly-lenient-adder.ngrok-free.app/gym/paypal-return/?membership_id={membership.id}",
                "cancel_url": f"https://broadly-lenient-adder.ngrok-free.app/gym/paypal-cancel/?membership_id={membership.id}"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": f"Membership: {membership.plan.name}",
                        "sku": "item",
                        "price": str(membership.plan.price),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(membership.plan.price),
                    "currency": "USD"
                },
                "description": f"Payment for {membership.plan.name}"
            }]
        })
        if payment.create():
            membership.tx_ref = payment.id
            membership.save()
            for link in payment.links:
                if link.rel == "approval_url":
                    return redirect(link.href)
        else:
            messages.error(self.request, 'Error initializing PayPal payment.')
            return redirect('membership_signup', plan_id=plan_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plan_id = self.kwargs.get('plan_id')
        selected_plan = get_object_or_404(MembershipPlan, id=plan_id)
        start_date = self.request.GET.get('start_date')
        context['plan'] = selected_plan  # Pass the selected plan to the template
        context['start_date'] = start_date  # Pass the start date to the template
        return context

    def handle_no_membership_found(self, request):
        messages.error(request, 'No membership found.')
        return redirect('my_memberships')








class CancelMembershipView(LoginRequiredMixin, View):
    def post(self, request, membership_id):
        membership = get_object_or_404(Membership, id=membership_id, user=request.user)
        membership.is_cancelled = True
        membership.status = 'cancelled'
        membership.save()
        messages.success(request, 'Membership has been cancelled successfully.')
        return redirect('my_memberships')

class MembershipSuccessView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        membership_id = self.kwargs['membership_id']
        membership = get_object_or_404(Membership, id=membership_id)
        membership.is_active = True
        membership.save()
        return redirect('my_memberships')

class MembershipCancelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        membership_id = self.kwargs['membership_id']
        membership = get_object_or_404(Membership, id=membership_id)
        membership.delete()
        return redirect('my_memberships')

class PayPalReturnView(View):
    def get(self, request, *args, **kwargs):
        payment_id = request.GET.get('paymentId')
        payer_id = request.GET.get('PayerID')
        membership = get_object_or_404(Membership, tx_ref=payment_id)

        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            MembershipPayment.objects.create(
                membership=membership,
                transaction_id=payment_id,
                amount=membership.plan.price,
                status='completed',
            )
            membership.status = 'active'
            membership.save()
            messages.success(request, 'Payment successful and membership activated.')
        else:
            messages.error(request, 'Payment failed. Please try again.')

        return redirect('my_memberships')

class PayPalCancelView(View):
    def get(self, request, *args, **kwargs):
        messages.warning(request, 'Payment cancelled.')
        return redirect('my_memberships')
