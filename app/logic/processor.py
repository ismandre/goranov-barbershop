from logic.state_machine import handle_state_transition


async def process_incoming_message(sender: str, message: str) -> str:
    """
    Receive WhatsApp message → Call business logic → Return reply string
    """

    reply = handle_state_transition(sender, message)

    return reply
