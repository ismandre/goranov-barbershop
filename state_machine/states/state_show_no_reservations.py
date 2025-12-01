from typing import override

from actions.action import Action
from actions.action_type import ActionType
from states.state import State
from states.state_await_no_reservation_action import StateAwaitNoReservationAction
from states.state_show_available_appointments import StateShowAvailableAppointments


class StateShowNoReservations(State):
    """
    User has no reservations; bot shows an empty reservation list.
    """

    @override
    def on_action(self, action: Action) -> State:
        if action.type == ActionType.ACTION_SHOW_AVAILABLE_APPOINTMENTS:
            return StateShowAvailableAppointments()

        return StateAwaitNoReservationAction()