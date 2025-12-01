from typing import override

from actions.action import Action
from states.state import State
from states.state_await_my_reservation_action import StateAwaitMyReservationAction


class StateShowMyReservations(State):
    """
    Bot shows the user’s existing reservations.
    """

    @override
    def on_action(self, action: Action) -> State:
        return StateAwaitMyReservationAction()