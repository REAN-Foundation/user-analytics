from abc import ABC, abstractmethod

###############################################################################

class IEventConsumer(ABC):

    @abstractmethod
    def start_listening(self) -> None:
        pass

    @abstractmethod
    def stop_listening(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
