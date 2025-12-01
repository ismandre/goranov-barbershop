from abc import ABC, abstractmethod


class Action(ABC):

    @property
    def type(self) -> str:
        return self.__class__.__name__