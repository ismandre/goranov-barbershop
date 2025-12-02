from twilio_handler.rest import Client
import os

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Twilio sandbox or approved number

client = Client(TWILIO_SID, TWILIO_TOKEN)

def send_whatsapp(to: str, message: str):
    client.messages.create(
        body=message,
        from_=WHATSAPP_NUMBER,
        to=f"whatsapp:{to}"
    )
