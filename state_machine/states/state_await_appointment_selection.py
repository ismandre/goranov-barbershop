from typing import override

from actions.action import Action
from actions.action_type import ActionType
from states.state import State


class StateAwaitAppointmentSelection(State):
    """
    Bot is waiting for the user to pick one of the listed available appointments.
    """


    @override
    def on_action(self, action: Action) -> State:
        if action.type == ActionType.ACTION_CONTINUE:
            from states.state_show_available_appointments import StateShowAvailableAppointments
            return StateShowAvailableAppointments()

        return self