from typing import override

from actions.action import Action
from state import State
from states.state_main_menu import StateMainMenu


class StateIdle(State):
    """
    Neutral state; bot is not engaged in any flow.
    """


    @override
    def on_action(self, action: Action) -> State:
        return StateMainMenu()