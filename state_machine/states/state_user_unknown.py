from typing import override

from actions.action import Action
from states.state import State
from states.state_main_menu import StateMainMenu


class StateUserUnknown(State):
    """
    User has never interacted before; onboarding / initial creation needed.
    """


    @override
    def on_action(self, action: Action) -> State:
        return StateMainMenu()