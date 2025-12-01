from typing import override

from actions.action import Action
from actions.action_type import ActionType
from state import State
from states.state_show_available_appointments import StateShowAvailableAppointments
from states.state_show_my_reservations import StateShowMyReservations
from states.state_show_no_reservations import StateShowNoReservations


class StateMainMenu(State):
    """
    User is at the starting menu: options to view available appointments or their reservations.
    """

    @override
    def on_action(self, action: Action) -> State:
        if action.type == ActionType.ACTION_SHOW_AVAILABLE_APPOINTMENTS:
            return StateShowAvailableAppointments()
        if action.type == ActionType.ACTION_SHOW_NO_RESERVATIONS:
            return StateShowNoReservations()
        if action.type == ActionType.ACTION_SHOW_EXISTING_RESERVATIONS:
            return StateShowMyReservations()

        return self