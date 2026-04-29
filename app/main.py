from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.messaging_response import MessagingResponse

from .logic.state_machine import handle_state_transition
from .api import auth, admin

app = FastAPI(
    title="Goranov Barbershop Bot",
    description="WhatsApp-based appointment booking system with admin API",
    version="1.0.0"
)

# CORS middleware (for admin dashboard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your dashboard domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Goranov Barbershop WhatsApp Bot is running",
        "version": "1.0.0"
    }


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
