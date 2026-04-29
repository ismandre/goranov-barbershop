from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

from .logic.state_machine import handle_state_transition

app = FastAPI(title="Goranov Barbershop Bot")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Goranov Barbershop WhatsApp Bot is running"}


@app.post("/whatsapp/webhook")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),       # WhatsApp sender phone number
    Body: str = Form(...),       # Actual WhatsApp text message
):
    """
    Twilio will push messages here using a POST request.
    Handles incoming WhatsApp messages and returns TwiML response.
    """
    print(f"📩 Incoming from {From}: {Body}")

    # Process message through state machine
    reply_text = handle_state_transition(sender=From, message=Body)

    print(f"📤 Replying: {reply_text[:100]}...")

    # Build WhatsApp response
    twiml = MessagingResponse()
    twiml.message(reply_text)

    return Response(content=str(twiml), media_type="application/xml")
