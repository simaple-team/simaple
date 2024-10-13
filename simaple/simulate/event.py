from abc import ABCMeta, abstractmethod
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

from pydantic import BaseModel

from simaple.core.base import Stat
from simaple.simulate.core import Action
from simaple.simulate.core.base import Event
from simaple.simulate.core.reducer import ReducerType
from simaple.simulate.core.store import Store
from simaple.simulate.reserved_names import Tag

T = TypeVar("T")


class EventProvider(metaclass=ABCMeta):
    @abstractmethod
    def elapsed(self, time: float) -> Event: ...

    @abstractmethod
    def rejected(self) -> Event: ...

    @abstractmethod
    def delayed(self, time: float) -> Event: ...

    @abstractmethod
    def dealt(
        self, damage: float, hit: float, modifier: Optional[Stat] = None
    ) -> Event: ...

    @abstractmethod
    def keydown_end(self) -> Event: ...

    @abstractmethod
    def wrap_reducer(self, reducer: ReducerType) -> ReducerType: ...

    @abstractmethod
    def wrap_with_modifier(self, event: Event) -> Event: ...


class NamedEventProvider(EventProvider):
    def __init__(self, name: str, default_modifier: Optional[Stat] = None):
        self._name = name
        self._default_modifier = default_modifier

    def wrap_reducer(self, reducer: ReducerType) -> ReducerType:
        @wraps(reducer)
        def wrapped_reducer(action: Action, store: Store) -> list[Event]:
            events = reducer(action, store)
            return [self.wrap_with_modifier(event) for event in events]

        return wrapped_reducer

    def wrap_response(
        self,
        state_and_events: tuple[T, list[Event]],
    ) -> tuple[T, list[Event]]:
        state, events = state_and_events

        return (state, [self.wrap_with_modifier(event) for event in events])

    def wrap_with_modifier(self, event: Event) -> Event:
        if event["tag"] == Tag.DOT:
            return event

        if event["tag"] != Tag.DAMAGE:
            return {
                **event,
                "name": self._name,
            }

        modifier = event["payload"].get("modifier", None)

        if self._default_modifier is None and modifier is None:
            total_modifier = None
        else:
            if self._default_modifier is None:
                total_modifier = modifier
            elif modifier is None:
                total_modifier = self._default_modifier
            else:
                total_modifier = Stat.model_validate(modifier) + self._default_modifier

        return {
            **event,
            "name": self._name,
            "payload": {
                **event["payload"],
                "modifier": total_modifier.model_dump() if total_modifier else None,
            },
        }

    def elapsed(self, time: float) -> Event:
        return {
            "name": self._name,
            "tag": Tag.ELAPSED,
            "payload": {"time": time},
            "method": "",
            "handler": None,
        }

    def rejected(self) -> Event:
        return {
            "name": self._name,
            "tag": Tag.REJECT,
            "payload": {},
            "method": "",
            "handler": None,
        }

    def delayed(self, time: float) -> Event:
        return {
            "name": self._name,
            "tag": Tag.DELAY,
            "payload": {"time": time},
            "method": "",
            "handler": None,
        }

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

        return {
            "name": self._name,
            "tag": Tag.DAMAGE,
            "payload": {
                "damage": damage,
                "hit": hit,
                "modifier": total_modifier.model_dump() if total_modifier else None,
            },
            "method": "",
            "handler": None,
        }

    def keydown_end(self) -> Event:
        return {
            "name": self._name,
            "tag": Tag.KEYDOWN_END,
            "payload": {},
            "method": "",
            "handler": None,
        }


_DEFAULT_EVENT_PROVIDER = NamedEventProvider("")


class EmptyEvent:
    @classmethod
    def elapsed(cls, time: float) -> Event:
        return _DEFAULT_EVENT_PROVIDER.elapsed(time)

    @classmethod
    def rejected(cls) -> Event:
        return _DEFAULT_EVENT_PROVIDER.rejected()

    @classmethod
    def delayed(cls, time: float) -> Event:
        return _DEFAULT_EVENT_PROVIDER.delayed(time)

    @classmethod
    def dealt(cls, damage: float, hit: float, modifier: Optional[Stat] = None) -> Event:
        return _DEFAULT_EVENT_PROVIDER.dealt(damage, hit, modifier)

    @classmethod
    def keydown_end(cls) -> Event:
        return _DEFAULT_EVENT_PROVIDER.keydown_end()


class DelayPayload(BaseModel):
    time: float
