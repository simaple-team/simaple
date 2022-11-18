from abc import ABCMeta, abstractmethod

from simaple.simulate.base import Event
from simaple.simulate.reserved_names import Tag


class EventProvider(metaclass=ABCMeta):
    @abstractmethod
    def elapsed(self, time: float) -> Event:
        ...

    @abstractmethod
    def rejected(self) -> Event:
        ...

    @abstractmethod
    def delayed(self, time: float) -> Event:
        ...

    @abstractmethod
    def dealt(self, damage: float, hit: float) -> Event:
        ...


class NamedEventProvider(EventProvider):
    def __init__(self, name: str):
        self._name = name

    def elapsed(self, time) -> Event:
        return Event(name=self._name, tag=Tag.ELAPSED, payload={"time": time})

    def rejected(self) -> Event:
        return Event(name=self._name, tag=Tag.REJECT)

    def delayed(self, time) -> Event:
        return Event(name=self._name, tag=Tag.DELAY, payload={"time": time})

    def dealt(self, damage: float, hit: float) -> Event:
        return Event(
            name=self._name,
            tag=Tag.DAMAGE,
            payload={
                "damage": damage,
                "hit": hit,
            },
        )
