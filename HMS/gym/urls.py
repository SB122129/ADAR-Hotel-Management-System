# urls.py
from django.urls import path
from .views import MembershipPlanListView, MembershipSignupView

urlpatterns = [
    path('membership-plans/', MembershipPlanListView.as_view(), name='membership_plans'),
    path('membership-signup/<int:plan_id>/', MembershipSignupView.as_view(), name='membership_signup'),
]
