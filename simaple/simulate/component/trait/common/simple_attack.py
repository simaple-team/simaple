from typing import TypedDict, TypeVar

from simaple.simulate.component.entity import Cooldown
from simaple.simulate.core import Event
from simaple.simulate.event import EmptyEvent
from simaple.simulate.global_property import Dynamics


class CoolDownState(TypedDict):
    cooldown: Cooldown
    dynamics: Dynamics


CoolDownStateT = TypeVar("CoolDownStateT", bound=CoolDownState)


class UseSimpleAttackPayload(TypedDict):
    cooldown_duration: float
    damage: float
    hit: float
    delay: float


def use(
    state: CoolDownStateT,
    cooldown_duration: float,
    damage: float,
    hit: float,
    delay: float,
) -> tuple[CoolDownStateT, list[Event]]:
    if not state["cooldown"].available:
        return state, [EmptyEvent.rejected()]

    state["cooldown"].set_time_left(
        state["dynamics"].stat.calculate_cooldown(cooldown_duration)
    )

    return state, [
        EmptyEvent.dealt(damage, hit),
        EmptyEvent.delayed(delay),
    ]


def elapse(state: CoolDownStateT, time: float) -> tuple[CoolDownStateT, list[Event]]:
    cooldown = state["cooldown"].model_copy()
    cooldown.elapse(time)
    state["cooldown"] = cooldown

    return state, [EmptyEvent.elapsed(time)]
