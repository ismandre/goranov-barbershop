from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.messaging_response import MessagingResponse

from .logic.state_machine import handle_state_transition
from .api import auth, admin
from .logging_config import setup_logging, get_logger
from .middleware.request_id import RequestIDMiddleware, RequestIDFilter

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Add request ID filter to all handlers
import logging
for handler in logging.getLogger().handlers:
    handler.addFilter(RequestIDFilter())

app = FastAPI(
    title="Goranov Barbershop Bot",
    description="WhatsApp-based appointment booking system with admin API",
    version="1.0.0"
)

# Request ID middleware (must be first)
app.add_middleware(RequestIDMiddleware)

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
    try:
        # Validate message length (Twilio limit is 1600 chars)
        if len(Body) > 1600:
            logger.warning(
                f"Message too long from {From}: {len(Body)} chars (truncating)",
                extra={"phone": From, "message_length": len(Body)}
            )
            Body = Body[:1600]

        logger.info(
            f"Incoming WhatsApp message from {From}",
            extra={"phone": From, "message_preview": Body[:100]}
        )

        # Process message through state machine
        reply_text = handle_state_transition(sender=From, message=Body)

        logger.info(
            f"Sending reply to {From}",
            extra={"phone": From, "reply_preview": reply_text[:100]}
        )

        # Build WhatsApp response
        twiml = MessagingResponse()
        twiml.message(reply_text)

        return Response(content=str(twiml), media_type="application/xml")

    except Exception as e:
        logger.error(
            f"Error processing WhatsApp message from {From}: {str(e)}",
            exc_info=True,
            extra={"phone": From, "message": Body}
        )

        # Return friendly error message to user (in Croatian)
        twiml = MessagingResponse()
        twiml.message(
            "Oprosti, dogodila se greška prilikom obrade tvoje poruke. "
            "Molim pokušaj ponovno za nekoliko trenutaka."
        )
        return Response(content=str(twiml), media_type="application/xml")
