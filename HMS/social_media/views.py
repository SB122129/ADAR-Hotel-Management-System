import re
import openai
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ChatBot
from .forms import ChatBotForm
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Custom_user, ChatMessage
from telegram import Bot
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import ChatMessage, Custom_user
from telegram import Bot
from room.models import *
from gym.models import *
from Hall.models import *
import re
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from django.db.models import Count, Sum



import google.generativeai as genai

# Configure the Gemini API key
genai.configure(api_key="AIzaSyBfK-J0sAekVr5GMfof-QjyiDlcuFCPaO8")



class ChatBotView(LoginRequiredMixin, FormView, ListView):
    model = ChatBot
    form_class = ChatBotForm
    template_name = 'social_media/chat.html'
    success_url = reverse_lazy('chat')
    context_object_name = 'chats'

    def get_queryset(self):
        return ChatBot.objects.filter(user=self.request.user).order_by('timestamp')

    def form_valid(self, form):
        user_message = form.cleaned_data['message']
        response_text = self.get_gemini_response(user_message)
        
        ChatBot.objects.create(
            user=self.request.user,
            message=user_message,
            response=response_text
        )
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"data": {"text": response_text}})
        return super().form_valid(form)

    def get_gemini_response(self, user_message):
        # Check for custom commands
        response_text = self.handle_custom_commands(user_message)
        if response_text:
            return response_text

        # If no custom commands, use Gemini response
        model = genai.GenerativeModel("gemini-pro")
        chat = model.start_chat()
        response = chat.send_message(user_message)
        
        # Assuming response.text contains the relevant response data
        response_content = response.text
        response_content = response_content.replace("\n", "<br>")
        formatted_response = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', response_content)
        
        return formatted_response

    def handle_custom_commands(self, user_message):
        user_message_lower = user_message.lower()

        if "available rooms" in user_message_lower:
            return self.get_available_rooms()

        if "pending bookings" in user_message_lower:
            return self.get_pending_bookings()

        if "total bookings" in user_message_lower:
            return self.get_total_bookings()

        if "total revenue by room type" in user_message_lower:
            return self.get_total_revenue_by_room_type()

        if "total revenue by hall type" in user_message_lower:
            return self.get_total_revenue_by_hall_type()

        if "total number of memberships" in user_message_lower:
            return self.get_total_memberships()

        if "booking trends" in user_message_lower:
            return self.get_booking_trends()

        if "room booking trends" in user_message_lower:
            return self.get_room_booking_trends()

        if "hall booking trends" in user_message_lower:
            return self.get_hall_booking_trends()

        return None

    def get_available_rooms(self):
        available_rooms = Room.objects.filter(room_status='vacant')
        response_text = "Available Rooms:<br>"
        for room in available_rooms:
            response_text += f"{room.room_number} - {room.room_type.name}<br>"
        return response_text

    def get_pending_bookings(self):
        pending_bookings = Booking.objects.filter(status='pending')
        response_text = "Pending Bookings:<br>"
        for booking in pending_bookings:
            response_text += f"Booking ID: {booking.id} - {booking.room.room_number} ({booking.room.room_type.name})<br>"
        return response_text

    def get_total_bookings(self):
        total_bookings = Booking.objects.count()
        return f"Total Bookings: {total_bookings}"

    def get_total_revenue_by_room_type(self):
        room_revenue = Room.objects.values('room_type__name').annotate(total_revenue=Sum('booking__total_amount'))
        response_text = "Total Revenue by Room Type:<br>"
        for room in room_revenue:
            response_text += f"{room['room_type__name']}: ETB {room['total_revenue']}<br>"
        return response_text

    def get_total_revenue_by_hall_type(self):
        hall_revenue = Hall.objects.values('hall_type__name').annotate(total_revenue=Sum('hall_booking__amount_due'))
        response_text = "Total Revenue by Hall Type:<br>"
        for hall in hall_revenue:
            response_text += f"{hall['hall_type__name']}: ETB {hall['total_revenue']}<br>"
        return response_text

    def get_total_memberships(self):
        memberships = Membership.objects.values('plan__name').annotate(total_members=Count('id'))
        response_text = "Total Memberships by Plan:<br>"
        for membership in memberships:
            response_text += f"{membership['plan__name']}: {membership['total_members']} memberships<br>"
        return response_text

    def get_booking_trends(self):
        # Example of booking trends over the last month
        one_month_ago = timezone.now() - timedelta(days=30)
        room_bookings = Booking.objects.filter(created_at__gte=one_month_ago).count()
        hall_bookings = Hall_Booking.objects.filter(created_at__gte=one_month_ago).count()

        response_text = f"Booking Trends in the Last Month:<br>Room Bookings: {room_bookings}<br>Hall Bookings: {hall_bookings}"
        return response_text

    def get_room_booking_trends(self):
        one_month_ago = timezone.now() - timedelta(days=30)
        room_bookings = Booking.objects.filter(created_at__gte=one_month_ago).values('created_at__date').annotate(count=Count('id'))
        
        response_text = "Room Booking Trends:<br>"
        for booking in room_bookings:
            response_text += f"{booking['created_at__date']}: {booking['count']} bookings<br>"
        return response_text

    def get_hall_booking_trends(self):
        one_month_ago = timezone.now() - timedelta(days=30)
        hall_bookings = Hall_Booking.objects.filter(created_at__gte=one_month_ago).values('created_at__date').annotate(count=Count('id'))
        
        response_text = "Hall Booking Trends:<br>"
        for booking in hall_bookings:
            response_text += f"{booking['created_at__date']}: {booking['count']} bookings<br>"
        return response_text






@csrf_exempt
def telegram_webhook(request):
    if request.method == "POST":
        data = json.loads(request.body)
        
        if "message" in data:
            message = data["message"]
            user_id = message["from"]["id"]
            username = message["from"]["username"]
            text = message["text"]

            # Create or get the user
            user, created = Custom_user.objects.get_or_create(telegram_id=user_id, defaults={'username': username})

            # Save the message
            ChatMessage.objects.create(user=user, message=text, timestamp=timezone.now())

        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "invalid request"}, status=400)


def send_message_to_telegram(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        message_text = request.POST.get("message")

        user = get_object_or_404(Custom_user, id=user_id)
        telegram_bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

        telegram_bot.send_message(chat_id=user.telegram_id, text=message_text)
        
        # Save the message in the ChatMessage model
        ChatMessage.objects.create(user=user, message=message_text, timestamp=timezone.now())

        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "invalid request"}, status=400)
