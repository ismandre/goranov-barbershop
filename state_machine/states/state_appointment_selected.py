from typing import override

from actions.action import Action
from actions.action_type import ActionType
from states.state import State
from states.state_confirm_appointment import StateConfirmAppointment
from states.state_idle import StateIdle


class StateAppointmentSelected(State):
    """
    User selected an appointment; bot confirms and prepares the booking.
    """

    @override
    def on_action(self, action: Action) -> State:
        if action.type == ActionType.ACTION_BOOK_APPOINTMENT:
            return StateIdle()

        return StateConfirmAppointment()