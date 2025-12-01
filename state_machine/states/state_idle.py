from typing import override

from actions.action import Action
from states.state import State

class StateIdle(State):
    """
    Neutral state; bot is not engaged in any flow.
    """


    @override
    def on_action(self, action: Action) -> State:
        from .state_main_menu import StateMainMenu
        return StateMainMenu()