from typing import override

from actions.action import Action
from actions.action_type import ActionType
from state import State
from states.state_appointment_selected import StateAppointmentSelected
from states.state_idle import StateIdle


class StateConfirmAppointment(State):
    """
    Bot asks the user to confirm or cancel the selected appointment.
    """

    @override
    def on_action(self, action: Action) -> State:
        if action.type == ActionType.ACTION_CONTINUE:
            return StateAppointmentSelected()
        if action.type == ActionType.ACTION_CANCEL:
            return StateIdle()

        return self