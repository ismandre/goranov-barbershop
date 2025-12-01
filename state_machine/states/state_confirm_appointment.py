from typing import override

from actions.action import Action
from actions.action_type import ActionType
from states.state import State
from states.state_idle import StateIdle


class StateConfirmAppointment(State):
    """
    Bot asks the user to confirm or cancel the selected appointment.
    """

    @override
    def on_action(self, action: Action) -> State:
        if action.type == ActionType.ACTION_CONTINUE:
            from states.state_appointment_selected import StateAppointmentSelected
            return StateAppointmentSelected()
        if action.type == ActionType.ACTION_CANCEL:
            return StateIdle()

        return self