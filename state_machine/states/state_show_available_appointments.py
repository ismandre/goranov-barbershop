from typing import override

from actions.action import Action
from actions.action_type import ActionType
from state import State
from states.state_appointment_selected import StateAppointmentSelected
from states.state_await_appointment_selection import StateAwaitAppointmentSelection


class StateShowAvailableAppointments(State):
    """
    Bot shows the list of available appointment slots.
    """


    @override
    def on_action(self, action: Action) -> State:
        if action.type == ActionType.ACTION_SELECT_APPOINTMENT:
            return StateAppointmentSelected()

        return StateAwaitAppointmentSelection()