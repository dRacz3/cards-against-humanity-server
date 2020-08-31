import abc
from abc import ABC

class IEventDispatcher(ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def setLogger(self, logger):
        pass

    @abc.abstractmethod
    def emit(self, message : str, event_name : str):
        pass
