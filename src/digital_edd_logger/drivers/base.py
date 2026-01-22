from abc import ABC, abstractmethod


class BaseDriver(ABC):

    @abstractmethod
    def send(self, record: dict) -> str:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
