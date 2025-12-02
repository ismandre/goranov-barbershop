from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

from logic.processor import process_incoming_message

app = FastAPI()


@app.post("/whatsapp/webhook")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),       # WhatsApp sender phone number
    Body: str = Form(...),       # Actual WhatsApp text message
):
    """
    Twilio will push messages here using a POST request.
    """

    print(f"Incoming from {From}: {Body}")

    # Your custom logic (state machine / NLU / AI / business logic)
    reply_text = await process_incoming_message(sender=From, message=Body)

    # Build WhatsApp response
    twiml = MessagingResponse()
    twiml.message(reply_text)

    return Response(content=str(twiml), media_type="application/xml")
