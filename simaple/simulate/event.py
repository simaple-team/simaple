from abc import ABCMeta, abstractmethod
from typing import Optional

from simaple.core.base import Stat
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
    def dealt(
        self, damage: float, hit: float, modifier: Optional[Stat] = None
    ) -> Event:
        ...

    @abstractmethod
    def keydown_end(self) -> Event:
        ...


class NamedEventProvider(EventProvider):
    def __init__(self, name: str, default_modifier: Optional[Stat] = None):
        self._name = name
        self._default_modifier = default_modifier

    def elapsed(self, time) -> Event:
        return Event(name=self._name, tag=Tag.ELAPSED, payload={"time": time})

    def rejected(self) -> Event:
        return Event(name=self._name, tag=Tag.REJECT)

    def delayed(self, time) -> Event:
        return Event(name=self._name, tag=Tag.DELAY, payload={"time": time})

    def dealt(
        self, damage: float, hit: float, modifier: Optional[Stat] = None
    ) -> Event:
        if self._default_modifier is None and modifier is None:
            total_modifier = None
        else:
            if self._default_modifier is None:
                total_modifier = modifier
            elif modifier is None:
                total_modifier = self._default_modifier
            else:
                total_modifier = modifier + self._default_modifier

        return Event(
            name=self._name,
            tag=Tag.DAMAGE,
            payload={
                "damage": damage,
                "hit": hit,
                "modifier": total_modifier.dict() if total_modifier else None,
            },
        )

    def keydown_end(self) -> Event:
        return Event(name=self._name, tag=Tag.KEYDOWN_END)
