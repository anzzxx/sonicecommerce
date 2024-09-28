import re
from twilio.rest import Client
from django.conf import settings
from twilio.base.exceptions import TwilioRestException

def send_otp(phone_number, otp):
    phone_number = format_phone_number(phone_number)
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    try:
        message = client.messages.create(
            body=f'Your OTP code is {otp}',
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return message.sid
    except TwilioRestException as e:
        # Handle the exception or log the error
        print(f"Failed to send OTP: {e}")
        return None

def format_phone_number(phone_number):
    # Replace any non-numeric characters
    phone_number = re.sub(r'\D', '', phone_number)
    # Ensure the phone number starts with a country code, e.g., +1 for USA
    if len(phone_number) > 10 and not phone_number.startswith('+'):
        phone_number = f"+{phone_number}"
    return phone_number
