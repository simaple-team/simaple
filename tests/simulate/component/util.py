from typing import Callable, TypeVar, Union

from simaple.simulate.base import Event
from simaple.simulate.component.base import ReducerState
from simaple.simulate.reserved_names import Tag


def count_damage_skill(events: list[Event]) -> int:
    return sum([e["tag"] == Tag.DAMAGE for e in events])


def compute_total_damage_coefficient(events: list[Event]) -> float:
    return sum(
        [
            e["payload"]["damage"] * e["payload"]["hit"]
            for e in events
            if e["tag"] == Tag.DAMAGE and e["payload"] is not None
        ]
    )


def total_delay(events: list[Event]) -> int:
    return sum(
        [
            e["payload"]["time"]
            for e in events
            if e["tag"] == Tag.DELAY and e["payload"] is not None
        ]
    )


def count_dot_skill(events: list[Event]) -> int:
    return sum([e["tag"] == Tag.DOT for e in events])


def is_rejected(events: list[Event]) -> bool:
    return events[0]["tag"] == Tag.REJECT


S = TypeVar("S", bound=ReducerState)


def pipe(
    initial_state: S, *args: Callable[[S], tuple[S, Union[Event, list[Event]]]]
) -> tuple[S, list[Event]]:
    state = initial_state
    total_events: list[Event] = []
    for fn in args:
        state, events = fn(state)

        if isinstance(events, list):
            total_events += events
        else:
            total_events += [events]

    return state, total_events
