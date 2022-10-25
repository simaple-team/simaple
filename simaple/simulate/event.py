from abc import ABCMeta, abstractmethod

from simaple.simulate.base import Event


class EventProvider(metaclass=ABCMeta):
    @abstractmethod
    def elapsed(self, time) -> Event:
        ...

    @abstractmethod
    def rejected(self) -> Event:
        ...

    @abstractmethod
    def delayed(self, time) -> Event:
        ...

    @abstractmethod
    def dealt(self, damage: float, hit: float, delay: float) -> Event:
        ...


class NamedEventProvider(EventProvider):
    def __init__(self, name: str):
        self._name = name

    def elapsed(self, time) -> Event:
        return Event(name=self._name, tag="global.elapsed", payload={"time": time})

    def rejected(self) -> Event:
        return Event(name=self._name, tag="global.reject")

    def delayed(self, time) -> Event:
        return Event(name=self._name, tag="global.delay", payload={"time": time})

    def dealt(self, damage: float, hit: float, delay: float) -> Event:
        return Event(
            name=self._name,
            tag="global.damage",
            payload={
                "damage": damage,
                "hit": hit,
                "delay": delay,
            },
        )
