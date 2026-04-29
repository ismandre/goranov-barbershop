"""State machine handler integrated with database."""

import sys
from pathlib import Path

# Add state_machine directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'state_machine'))

from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.user_service import UserService
from app.services.appointment_service import AppointmentService
from app.logic.intent_parser import IntentParser
from app.logic.messages import Messages

from states.state import State
from states.state_user_unknown import StateUserUnknown
from states.state_main_menu import StateMainMenu
from states.state_show_available_appointments import StateShowAvailableAppointments
from states.state_show_my_reservations import StateShowMyReservations
from states.state_show_no_reservations import StateShowNoReservations
from states.state_await_appointment_selection import StateAwaitAppointmentSelection
from states.state_appointment_selected import StateAppointmentSelected
from states.state_confirm_appointment import StateConfirmAppointment
from states.state_await_my_reservation_action import StateAwaitMyReservationAction
from states.state_await_no_reservation_action import StateAwaitNoReservationAction
from states.state_idle import StateIdle

from actions.action_user_message import ActionUserMessage
from actions.action_show_available_appointments import ActionShowAvailableAppointments
from actions.action_show_existing_reservations import ActionShowExistingReservations
from actions.actions_show_no_reservations import ActionsShowNoReservations
from actions.action_select_appointment import ActionSelectAppointment
from actions.action_continue import ActionContinue
from actions.action_cancel import ActionCancel
from actions.action_book_appointment import ActionBookAppointment


# Map state names to state classes
STATE_CLASSES = {
    'StateUserUnknown': StateUserUnknown,
    'StateMainMenu': StateMainMenu,
    'StateShowAvailableAppointments': StateShowAvailableAppointments,
    'StateShowMyReservations': StateShowMyReservations,
    'StateShowNoReservations': StateShowNoReservations,
    'StateAwaitAppointmentSelection': StateAwaitAppointmentSelection,
    'StateAppointmentSelected': StateAppointmentSelected,
    'StateConfirmAppointment': StateConfirmAppointment,
    'StateAwaitMyReservationAction': StateAwaitMyReservationAction,
    'StateAwaitNoReservationAction': StateAwaitNoReservationAction,
    'StateIdle': StateIdle,
}

# Map action types to action classes
ACTION_CLASSES = {
    'ACTION_USER_MESSAGE': ActionUserMessage,
    'ACTION_SHOW_AVAILABLE_APPOINTMENTS': ActionShowAvailableAppointments,
    'ACTION_SHOW_EXISTING_RESERVATIONS': ActionShowExistingReservations,
    'ACTION_SHOW_NO_RESERVATIONS': ActionsShowNoReservations,
    'ACTION_SELECT_APPOINTMENT': ActionSelectAppointment,
    'ACTION_CONTINUE': ActionContinue,
    'ACTION_CANCEL': ActionCancel,
    'ACTION_BOOK_APPOINTMENT': ActionBookAppointment,
}


def handle_state_transition(sender: str, message: str) -> str:
    """
    Handle incoming message and return response.

    Args:
        sender: WhatsApp phone number (e.g., 'whatsapp:+385123456789')
        message: User's message text

    Returns:
        Response message to send back to user
    """
    # Clean phone number (remove 'whatsapp:' prefix if present)
    phone_number = sender.replace('whatsapp:', '')

    with get_db() as db:
        # Get or create user
        user = UserService.get_or_create_user(db, phone_number)

        # Log incoming message
        UserService.log_message(db, user.id, message, is_from_user=True)

        # Get user's current state
        user_state = UserService.get_user_state(db, user.id)
        context = UserService.get_state_context(user_state)

        # Determine current state (default to UserUnknown for new users)
        if user_state:
            current_state = _instantiate_state(user_state.current_state)
        else:
            current_state = StateUserUnknown()
            context['first_time'] = True

        # Parse message to determine action (with context awareness)
        current_state_name = current_state.__class__.__name__
        action_type = IntentParser.parse_message(message, current_state_name)
        action = _instantiate_action(action_type)

        # Execute state transition
        next_state, response = _execute_transition(
            db, user.id, current_state, action, action_type, message, context
        )

        # Save new state
        new_context = _update_context(context, message, action_type, next_state)
        UserService.set_user_state(db, user.id, next_state.__class__.__name__, new_context)

        # Log response
        UserService.log_message(db, user.id, response, is_from_user=False)

        return response


def _instantiate_state(state_name: str) -> State:
    """Instantiate a state class from its name."""
    state_class = STATE_CLASSES.get(state_name, StateMainMenu)
    return state_class()


def _instantiate_action(action_type: str):
    """Instantiate an action class from its type."""
    action_class = ACTION_CLASSES.get(action_type, ActionUserMessage)
    return action_class()


def _execute_transition(
    db: Session,
    user_id: int,
    current_state: State,
    action,
    action_type: str,
    message: str,
    context: dict
) -> Tuple[State, str]:
    """
    Execute state transition and generate response.

    Returns:
        Tuple of (next_state, response_message)
    """
    current_state_name = current_state.__class__.__name__

    # Get next state from state machine
    next_state = current_state.on_action(action)
    next_state_name = next_state.__class__.__name__

    # Special case: Booking confirmation flow
    # StateConfirmAppointment + ACTION_BOOK_APPOINTMENT → book and go to idle
    # OR StateAppointmentSelected + ACTION_BOOK_APPOINTMENT → book and go to idle
    if (action_type == 'ACTION_BOOK_APPOINTMENT' and
        current_state_name in ['StateConfirmAppointment', 'StateAppointmentSelected']):
        # Book the appointment
        slot_id = context.get('selected_slot_id')
        if slot_id:
            appointment = AppointmentService.book_appointment(db, user_id, slot_id)
            if appointment:
                context.pop('selected_slot_id', None)
                context.pop('available_slots', None)
                response = Messages.booking_confirmed(appointment.slot)
                # Transition to Idle after successful booking
                next_state = StateIdle()
                return next_state, response
            else:
                response = Messages.slot_no_longer_available()
                next_state = StateIdle()
                return next_state, response

    # Generate appropriate response based on new state
    response = _generate_response(db, user_id, next_state, action_type, message, context)

    return next_state, response


def _generate_response(
    db: Session,
    user_id: int,
    state: State,
    action_type: str,
    message: str,
    context: dict
) -> str:
    """Generate response message based on current state."""
    state_name = state.__class__.__name__

    if state_name == 'StateUserUnknown':
        return Messages.welcome()

    elif state_name == 'StateMainMenu':
        # Check if this is first interaction (coming from UserUnknown)
        if context.get('first_time', False):
            context['first_time'] = False
            return Messages.welcome()
        return Messages.main_menu()

    elif state_name == 'StateShowAvailableAppointments':
        slots = AppointmentService.get_available_slots(db, limit=10)
        # Store slots in context for later reference
        context['available_slots'] = [slot.id for slot in slots]
        return Messages.show_available_slots(slots)

    elif state_name == 'StateAwaitAppointmentSelection':
        # User needs to select from available slots
        return Messages.invalid_choice()

    elif state_name == 'StateAppointmentSelected':
        # User just selected a slot - show confirmation
        slot_number = IntentParser.extract_number(message)
        available_slot_ids = context.get('available_slots', [])

        if slot_number and 1 <= slot_number <= len(available_slot_ids):
            slot_id = available_slot_ids[slot_number - 1]
            slot = AppointmentService.get_slot_by_id(db, slot_id)

            if slot and not slot.is_booked:
                context['selected_slot_id'] = slot_id
                return Messages.confirm_booking(slot)
            else:
                return Messages.slot_no_longer_available()
        else:
            return Messages.invalid_slot_number()

    elif state_name == 'StateConfirmAppointment':
        # Re-show confirmation (booking is handled in _execute_transition)
        slot_id = context.get('selected_slot_id')
        if slot_id:
            slot = AppointmentService.get_slot_by_id(db, slot_id)
            if slot:
                return Messages.confirm_booking(slot)
        return Messages.error()

    elif state_name == 'StateShowMyReservations':
        appointments = AppointmentService.get_active_appointments(db, user_id)
        context['my_appointments'] = [appt.id for appt in appointments]
        return Messages.show_my_reservations(appointments)

    elif state_name == 'StateShowNoReservations':
        return Messages.no_reservations()

    elif state_name == 'StateAwaitMyReservationAction':
        return Messages.invalid_choice()

    elif state_name == 'StateAwaitNoReservationAction':
        return Messages.invalid_choice()

    elif state_name == 'StateIdle':
        return Messages.main_menu()

    else:
        return Messages.error()


def _update_context(
    context: dict,
    message: str,
    action_type: str,
    next_state: State
) -> dict:
    """Update context based on action and state transition."""
    # Context is mutable, modifications are already made in _generate_response
    # Just ensure we return it
    return context
