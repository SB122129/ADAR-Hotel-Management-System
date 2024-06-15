import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler
import requests
import random
import string
from datetime import datetime
from django.utils import timezone
from room.models import Booking, Room, Payment
from accountss.models import Custom_user
import paypalrestsdk
from room.forms import BookingForm  # Adjust the import according to your project structure

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# States
EMAIL, CHECK_IN_DATE, CHECK_OUT_DATE, GUESTS, PAYMENT_METHOD = range(5)

# Command to start the conversation
def start(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        'Welcome! Please enter your email to start booking:'
    )
    return EMAIL

def email(update: Update, context: CallbackContext) -> int:
    email = update.message.text
    try:
        user = Custom_user.objects.get(email=email)
        user.telegram_user_id = update.message.from_user.id
        user.save()
    except Custom_user.DoesNotExist:
        update.message.reply_text('Email not found. Please register first.')
        return ConversationHandler.END
    
    context.user_data['user'] = user
    update.message.reply_text(
        'Email verified! Please enter your check-in date (YYYY-MM-DD):'
    )
    return CHECK_IN_DATE

def check_in_date(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    user_data['check_in_date'] = update.message.text
    update.message.reply_text(
        'Great! Now, please enter your check-out date (YYYY-MM-DD):'
    )
    return CHECK_OUT_DATE

def check_out_date(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    user_data['check_out_date'] = update.message.text
    update.message.reply_text(
        'Almost there! How many guests will be staying?'
    )
    return GUESTS

def guests(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    user_data['guests'] = int(update.message.text)
    room_id = 1  # Replace with actual room ID
    room = Room.objects.get(id=room_id)

    # Validate the input here
    form = BookingForm(data=user_data, room=room)
    if form.is_valid():
        context.user_data['room'] = room
        keyboard = [
            [InlineKeyboardButton("Chapa", callback_data='chapa')],
            [InlineKeyboardButton("PayPal", callback_data='paypal')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            'Please select a payment method:',
            reply_markup=reply_markup
        )
        return PAYMENT_METHOD
    else:
        update.message.reply_text(
            'Invalid data. Please start over by entering /start.'
        )
        return ConversationHandler.END

def payment_method(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    payment_method = query.data
    user_data = context.user_data
    user = user_data['user']

    # Create the booking instance
    booking = Booking(
        user=user,
        room=user_data['room'],
        check_in_date=user_data['check_in_date'],
        check_out_date=user_data['check_out_date'],
        guests=user_data['guests'],
        status='pending',
        tx_ref=f"{user.first_name}-tx-{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}"
    )
    booking.save()
    user_data['booking'] = booking

    if payment_method == 'chapa':
        return process_chapa_payment(update, context)
    elif payment_method == 'paypal':
        return process_paypal_payment(update, context)

def process_chapa_payment(update: Update, context: CallbackContext) -> int:
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
    data = response.json()
    if response.status_code == 200:
        checkout_url = data['data']['checkout_url']
        update.callback_query.message.reply_text(f'Please complete the payment: {checkout_url}')
    else:
        update.callback_query.message.reply_text('Error initializing payment.')

    return ConversationHandler.END

def process_paypal_payment(update: Update, context: CallbackContext) -> int:
    booking = context.user_data['booking']
    paypalrestsdk.configure({
        "mode": "sandbox",  # sandbox or live
        "client_id": "ARbeUWx-il1YsBMeVLQpy2nFI4l3vsuwipJXyhWo1Bmee4YYyuxQWrzX7joSU0IZfytEJ4s3rteXh5kj",
        "client_secret": "EFph5hrjs9Pok_vmU3JbkY2RVZ0FA8HlG-uhkEytPrxn6k1YwWz6_t4ph03eesiYTFhsYsgJgyRYkLuF"
    })

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": f"https://4302-102-218-50-52.ngrok-free.app/room/paypal-return/?booking_id={booking.id}",
            "cancel_url": f"https://4302-102-218-50-52.ngrok-free.app/room/paypal-cancel/?booking_id={booking.id}"
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "room booking",
                    "sku": "item",
                    "price": str(booking.total_amount),
                    "currency": "USD",
                    "quantity": 1}]
            },
            "amount": {"total": str(booking.total_amount), "currency": "USD"},
            "description": "This is the payment transaction description."
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = link.href
                break
        update.callback_query.message.reply_text(f'Please complete the payment: {approval_url}')
    else:
        update.callback_query.message.reply_text('Error creating PayPal payment.')

    return ConversationHandler.END

def cancel(update: Update, _: CallbackContext) -> int:
    update.message.reply_text('Booking cancelled. To start over, type /start.')
    return ConversationHandler.END

def main() -> None:
    """Start the bot."""
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN")

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            EMAIL: [MessageHandler(Filters.text & ~Filters.command, email)],
            CHECK_IN_DATE: [MessageHandler(Filters.text & ~Filters.command, check_in_date)],
            CHECK_OUT_DATE: [MessageHandler(Filters.text & ~Filters.command, check_out_date)],
            GUESTS: [MessageHandler(Filters.text & ~Filters.command, guests)],
            PAYMENT_METHOD: [CallbackQueryHandler(payment_method)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
