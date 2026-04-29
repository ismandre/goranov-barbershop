"""Parse user messages to determine intent/action."""

import re
from typing import Optional


class IntentParser:
    """Simple keyword-based intent recognition."""

    # Croatian and English keywords for each intent
    SHOW_AVAILABLE = [
        'dostupno', 'dostupni', 'slobodno', 'slobodni', 'rezerviraj',
        'termin', 'termine', 'available', 'book', 'appointment'
    ]

    MY_RESERVATIONS = [
        'moje', 'moja', 'rezervacije', 'rezervacija', 'termini',
        'my', 'reservations', 'appointments'
    ]

    CONTINUE = [
        'da', 'yes', 'nastavi', 'continue', 'proceed', 'potvrdi', 'confirm'
    ]

    CANCEL = [
        'ne', 'no', 'odustani', 'cancel', 'back', 'natrag', 'otkaži'
    ]

    @staticmethod
    def parse_message(message: str, current_state: str = None) -> str:
        """
        Parse user message and return action type.

        Args:
            message: User's message text
            current_state: Optional current state name for context-aware parsing

        Returns:
            Action type as string, or 'ACTION_USER_MESSAGE' if unknown
        """
        message_lower = message.lower().strip()

        # Check for show available appointments
        if any(keyword in message_lower for keyword in IntentParser.SHOW_AVAILABLE):
            return 'ACTION_SHOW_AVAILABLE_APPOINTMENTS'

        # Check for my reservations
        if any(keyword in message_lower for keyword in IntentParser.MY_RESERVATIONS):
            return 'ACTION_SHOW_EXISTING_RESERVATIONS'

        # Check for continue/confirm
        if any(keyword in message_lower for keyword in IntentParser.CONTINUE):
            # If user is in appointment selection/confirmation state, treat as "book"
            if current_state in ['StateConfirmAppointment', 'StateAppointmentSelected']:
                return 'ACTION_BOOK_APPOINTMENT'
            return 'ACTION_CONTINUE'

        # Check for cancel
        if any(keyword in message_lower for keyword in IntentParser.CANCEL):
            return 'ACTION_CANCEL'

        # Context-aware number parsing
        if re.match(r'^\d+$', message_lower):
            # At main menu, "1" = show available, "2" = my reservations
            if current_state == 'StateMainMenu':
                num = int(message_lower)
                if num == 1:
                    return 'ACTION_SHOW_AVAILABLE_APPOINTMENTS'
                elif num == 2:
                    return 'ACTION_SHOW_EXISTING_RESERVATIONS'
            # In other states, numbers are selections
            else:
                return 'ACTION_SELECT_APPOINTMENT'

        # Default: user message (trigger main menu for new users)
        return 'ACTION_USER_MESSAGE'

    @staticmethod
    def extract_number(message: str) -> Optional[int]:
        """Extract number from message (for slot selection)."""
        match = re.search(r'\d+', message)
        return int(match.group()) if match else None
