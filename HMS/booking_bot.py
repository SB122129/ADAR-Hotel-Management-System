import asyncio
from datetime import datetime, date
from threading import Thread
import requests
import logging
import paypalrestsdk
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from telegram import Update
import json
import random,string
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from room.models import Room, Booking
from accountss.models import Custom_user

logger = logging.getLogger(__name__)

# Define states
EMAIL, MENU, ROOM_SELECTION, CHECK_IN_DATE, CHECK_OUT_DATE, GUESTS, PAYMENT_METHOD, MY_BOOKINGS, PENDING_PAYMENT_PROCESS = range(9)

# Helper function to generate the main menu buttons
def get_main_menu_buttons():
    buttons = [
        [InlineKeyboardButton("Start Booking", callback_data='start_booking')],
        [InlineKeyboardButton("My Bookings", callback_data='my_bookings')],
        [InlineKeyboardButton("Pending Payments", callback_data='pending_payments')],
        [InlineKeyboardButton("Restart", callback_data='restart')]
    ]
    return InlineKeyboardMarkup(buttons)

# Command to start the conversation and ask for email
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Please enter your email:')
    return EMAIL

# Handle email input
async def email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    email = update.message.text
    user = await sync_to_async(Custom_user.objects.filter(email=email).first)()

    if user:
        user.telegram_user_id = update.message.from_user.id
        await sync_to_async(user.save)()
    else:
        await update.message.reply_text('Email not found. Please enter your email again .')
        return EMAIL

    context.user_data['user'] = user

    await update.message.reply_text(
        'Welcome to Room Booking Bot! Please select an option:',
        reply_markup=get_main_menu_buttons()
    )
    return MENU

# Handle menu selection
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    action = query.data

    if action == 'start_booking':
        return await start_booking(update, context)
    elif action == 'my_bookings':
        return await my_bookings(update, context)
    elif action == 'pending_payments':
        return await pending_payments(update, context)
    elif action == 'restart':
        return await restart_bot(update, context)

# Start the booking process
async def start_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    available_rooms = await sync_to_async(Room.objects.filter)(room_status='vacant')
    keyboard = []

    for room in available_rooms:
        button_text = f"{room.room_number} - {room.room_type.name}\nPrice: ${room.price_per_night}\n"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=str(room.id))])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text('Please select a room:', reply_markup=reply_markup)
    return ROOM_SELECTION

# Handle room selection
async def room_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    room_id = int(query.data)
    room = await sync_to_async(Room.objects.get)(id=room_id)
    context.user_data['room'] = room

    await query.message.reply_text(
        f'You selected Room {room.room_number}\nType: {room.room_type.name}\nPrice: ${room.price_per_night}\nCapacity: {room.capacity}\n\nPlease enter your check-in date (YYYY-MM-DD):',
    )
    return CHECK_IN_DATE

# Handle check-in date input
async def check_in_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    check_in_date_str = update.message.text

    try:
        check_in_date = datetime.strptime(check_in_date_str, '%Y-%m-%d').date()

        if check_in_date < date.today():
            await update.message.reply_text(
                'Check-in date cannot be in the past. Please enter a valid check-in date:',
            )
            return CHECK_IN_DATE

        user_data['check_in_date'] = check_in_date
    except ValueError:
        await update.message.reply_text(
            'Invalid date format. Please use YYYY-MM-DD. Enter again, example 2022-12-31.',
        )
        return CHECK_IN_DATE

    await update.message.reply_text(
        'Great! Now, please enter your check-out date (YYYY-MM-DD):',
    )
    return CHECK_OUT_DATE

# Handle check-out date input
async def check_out_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    check_out_date_str = update.message.text

    try:
        check_out_date = datetime.strptime(check_out_date_str, '%Y-%m-%d').date()

        if check_out_date <= user_data['check_in_date']:
            await update.message.reply_text(
                'Check-out date must be after the check-in date. Please renter a valid check-out date:',
            )
            return CHECK_OUT_DATE

        user_data['check_out_date'] = check_out_date
    except ValueError:
        await update.message.reply_text(
            'Invalid date format. Please use YYYY-MM-DD. Enter again, example 2022-12-31.',
        )
        return CHECK_OUT_DATE

    await update.message.reply_text(
        'Almost there! How many guests will be staying?',
    )
    return GUESTS

# Handle guests input
async def guests(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    guests_str = update.message.text

    try:
        guests = int(guests_str)
        room_capacity = user_data['room'].capacity

        if guests < 1:
            await update.message.reply_text(
                'The number of guests must be at least 1. Please enter a valid number of guests:',
            )
            return GUESTS
        elif guests > room_capacity:
            await update.message.reply_text(
                f'The number of guests cannot exceed the room capacity which is {room_capacity} for this room. Please enter a valid number of guests:',
            )
            return GUESTS

        user_data['guests'] = guests
    except ValueError:
        await update.message.reply_text(
            'Invalid input. Please enter a number.',
        )
        return GUESTS

    keyboard = [
        [InlineKeyboardButton("Chapa", callback_data='chapa')],
        [InlineKeyboardButton("PayPal", callback_data='paypal')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'Please select a payment method:',
        reply_markup=reply_markup
    )

    return PAYMENT_METHOD

# Handle payment method selection
async def payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    payment_method = query.data
    user_data = context.user_data
    user = user_data['user']

    booking = await sync_to_async(Booking.objects.create)(
        user=user,
        room=user_data['room'],
        check_in_date=user_data['check_in_date'],
        check_out_date=user_data['check_out_date'],
        guests=user_data['guests'],
        tx_ref=f"{user.first_name}-tx-{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}",
        total_amount=user_data['room'].price_per_night * (user_data['check_out_date'] - user_data['check_in_date']).days
    )
    user_data['booking'] = booking

    if payment_method == 'chapa':
        await query.message.reply_text('Please proceed with Chapa payment.')
        booking = context.user_data['booking']
        amount = str(booking.total_amount)
        tx_ref = booking.tx_ref
        redirect_url = f'https://4302-102-218-50-52.ngrok-free.app/room/bookings'
        webhook_url = f'https://4302-102-218-50-52.ngrok-free.app/room/chapa-webhook/'

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

        response = requests.post("https://api.chapa.co/v1/transaction/initialize", json=payload, headers=headers)
        result = response.json()

        if response.status_code == 200:
            checkout_url = result['data']['checkout_url']
            await update.callback_query.message.reply_text(f'Please complete the payment: {checkout_url}')
        else:
            await update.callback_query.message.reply_text('Error creating Chapa payment.')

        await update.callback_query.message.reply_text(
            'What would you like to do next?',
            reply_markup=get_main_menu_buttons()
        )
        return MENU

    elif payment_method == 'paypal':
        paypalrestsdk.configure({
            "mode": "sandbox",
            "client_id": "ARbeUWx-il1YsBMeVLQpy2nFI4l3vsuwipJXyhWo1Bmee4YYyuxQWrzX7joSU0IZfytEJ4s3rteXh5kj",
            "client_secret": "EFph5hrjs9Pok_vmU3JbkY2RVZ0FA8HlG-uhkEytPrxn6k1YwWz6_t4ph03eesiYTFhsYsgJgyRYkLuF"
        })

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": f"https://4302-102-218-50-52.ngrok-free.app/room/paypal-return/?booking_id={booking.id}",
                "cancel_url": f"https://4302-102-218-50-52.ngrok-free.app/room/paypal-cancel/?booking_id={booking.id}"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": f"Booking {booking.id}",
                        "sku": "001",
                        "price": str(booking.total_amount),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(booking.total_amount),
                    "currency": "USD"
                },
                "description": "Room booking payment."
            }]
        })

        if payment.create():
            for link in payment.links:
                if link.method == "REDIRECT":
                    approval_url = str(link.href)
                    await query.message.reply_text(f'Please complete the payment: {approval_url}')
        else:
            await query.message.reply_text('Error creating PayPal payment.')

    await query.message.reply_text(
        'What would you like to do next?',
        reply_markup=get_main_menu_buttons()
    )
    return MENU

# Handle user's bookings
async def my_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    user = context.user_data.get('user')

    if not user:
        await query.message.reply_text('User not found. Please restart the bot and enter your email.')
        return ConversationHandler.END

    try:
        bookings = await sync_to_async(list)(Booking.objects.filter(user=user).exclude(status__in=['cancelled']))

        if not bookings:
            await query.message.reply_text('You have no bookings.')
            return MENU

        for booking in bookings:
            room = booking.room
            message = (
                f"Booking ID: {booking.id}\n"
                f"Room Number: {room.room_number}\n"
                f"Room Type: {room.room_type.name}\n"
                f"Check-in Date: {booking.check_in_date}\n"
                f"Check-out Date: {booking.check_out_date}\n"
                f"Total Amount: ${booking.total_amount}\n"
                f"Payment Status: {booking.status}\n\n"
            )
            await query.message.reply_text(message)

        await query.message.reply_text(
            'What would you like to do next?',
            reply_markup=get_main_menu_buttons()
        )
        return MENU

    except Exception as e:
        logger.error(f"Error fetching bookings: {e}")
        await query.message.reply_text('An error occurred while fetching your bookings. Please try again later.',reply_markup=get_main_menu_buttons())
        return MENU

# Handle user's pending payments
async def pending_payments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    user = context.user_data.get('user')

    if not user:
        await query.message.reply_text('User not found. Please restart the bot and enter your email.')
        return ConversationHandler.END

    try:
        bookings = await sync_to_async(list)(Booking.objects.filter(user=user, status='pending'))

        if not bookings:
            await query.message.reply_text('You have no pending payments.')
            return MENU

        for booking in bookings:
            room = booking.room
            message = (
                f"Booking ID: {booking.id}\n"
                f"Room Number: {room.room_number}\n"
                f"Room Type: {room.room_type.name}\n"
                f"Check-in Date: {booking.check_in_date}\n"
                f"Check-out Date: {booking.check_out_date}\n"
                f"Total Amount: ${booking.total_amount}\n"
                f"Payment Status: {booking.status}\n\n"
            )
            await query.message.reply_text(
                message,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Pay Now", callback_data=f'pay_pending_{booking.id}')]
                ])
            )

        return PENDING_PAYMENT_PROCESS

    except Exception as e:
        logger.error(f"Error fetching pending payments: {e}")
        await query.message.reply_text('An error occurred while fetching your pending payments. Please try again later.', reply_markup=get_main_menu_buttons())
        return MENU

# Handle "Pay Now" button click for pending payments
async def pay_pending(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    # Extract booking ID from callback data
    callback_data = query.data
    booking_id = int(callback_data.split('_')[-1])
    
    # Find the booking with the given ID
    booking = await sync_to_async(Booking.objects.get)(id=booking_id)
    context.user_data['booking'] = booking
    
    # Provide payment options again
    keyboard = [
        [InlineKeyboardButton("Chapa", callback_data='chapa')],
        [InlineKeyboardButton("PayPal", callback_data='paypal')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        'Please select a payment method to complete your pending payment:',
        reply_markup=reply_markup
    )
    
    return PAYMENT_METHOD

# Handle cancellation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        'Booking cancelled. To start over, type /start.',
        reply_markup=get_main_menu_buttons()
    )
    return ConversationHandler.END

# Handle bot restart
async def restart_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        'Bot is restarting. To start over, type /start.',
        reply_markup=get_main_menu_buttons()
    )
    return EMAIL

# Main function to run the bot
def main():
    application = Application.builder().token('YOUR_BOT_TOKEN').build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
            MENU: [CallbackQueryHandler(menu)],
            ROOM_SELECTION: [CallbackQueryHandler(room_selection)],
            CHECK_IN_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_in_date)],
            CHECK_OUT_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_out_date)],
            GUESTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, guests)],
            PAYMENT_METHOD: [CallbackQueryHandler(payment_method)],
            MY_BOOKINGS: [CallbackQueryHandler(my_bookings)],
            PENDING_PAYMENT_PROCESS: [CallbackQueryHandler(pay_pending)]
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            MessageHandler(filters.TEXT & ~filters.COMMAND, restart_bot)
        ],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
