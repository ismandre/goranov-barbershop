from typing import override

from actions.action import Action
from actions.action_type import ActionType
from states.state import State
from states.state_idle import StateIdle
from states.state_show_available_appointments import StateShowAvailableAppointments


class StateAwaitNoReservationAction(State):
    """
    Bot prompts user what to do next after showing they have no reservations.
    """

    @override
    def on_action(self, action: Action) -> State:
        if action.type == ActionType.ACTION_CONTINUE:
            return StateShowAvailableAppointments()
        if action.type == ActionType.ACTION_CANCEL:
            return StateIdle()

        raise Exception('Unhandled action type: ' + str(action.type))