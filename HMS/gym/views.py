# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, FormView
from .models import MembershipPlan, Membership, MembershipPayment
from .forms import MembershipSignupForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
import requests
import random
import string

class MembershipPlanListView(ListView):
    model = MembershipPlan
    template_name = 'membership_plans.html'
    context_object_name = 'plans'

class MembershipSignupView(LoginRequiredMixin, FormView):
    template_name = 'membership_signup.html'
    form_class = MembershipSignupForm
    success_url = '/my-memberships/'  # Redirect to a page that shows user memberships

    def form_valid(self, form):
        plan = get_object_or_404(MembershipPlan, id=self.kwargs['plan_id'])
        user = self.request.user
        membership = Membership.objects.create(user=user, plan=plan, is_active=True)

        amount = plan.price
        tx_ref = f"{user.username}-tx-{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}"

        payload = {
            "amount": str(amount),
            "currency": "ETB",
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "tx_ref": tx_ref,
            "customization": {
                "title": "Gym Membership Payment",
                "description": f"Payment for {plan.name}"
            }
        }
        headers = {
            'Authorization': 'CHASECK_TEST-TdJi1iOZAzK5F6rH4BpAQr58fqyF3sRk',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post("https://api.chapa.co/v1/transaction/initialize", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            # Handle the response data as needed
            # Save the payment record
            MembershipPayment.objects.create(
                membership=membership,
                transaction_id=tx_ref,
                amount=amount,
                status='pending',  # Assuming payment is pending until confirmed
                payment_method='chapa'
            )
            return redirect(self.success_url)
        except requests.RequestException as e:
            return HttpResponseBadRequest(f"Error with Chapa payment: {e}")

    def form_invalid(self, form):
        return HttpResponseBadRequest("Invalid form data.")
