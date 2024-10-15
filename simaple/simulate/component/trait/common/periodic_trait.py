from typing import TypedDict, TypeVar

from simaple.simulate.component.entity import Cooldown, Periodic
from simaple.simulate.component.view import KeydownView, Running, Validity
from simaple.simulate.core import Event
from simaple.simulate.event import EmptyEvent
from simaple.simulate.global_property import Dynamics


class _State(TypedDict):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


_StateT = TypeVar("_StateT", bound=_State)


def start_periodic_with_cooldown(
    state: _StateT,
    damage: float,
    hit: float,
    delay: float,
    cooldown_duration: float,
    lasting_duration: float,
) -> tuple[_StateT, list[Event]]:
    """use_periodic_damage_trait"""
    cooldown, periodic = (
        state["cooldown"].model_copy(),
        state["periodic"].model_copy(),
    )

    if not cooldown.available:
        return state, [EmptyEvent.rejected()]

    cooldown.set_time_left(state["dynamics"].stat.calculate_cooldown(cooldown_duration))
    periodic.set_time_left(lasting_duration)

    state["cooldown"] = cooldown
    state["periodic"] = periodic

    return state, [
        EmptyEvent.dealt(damage, hit),
        EmptyEvent.delayed(delay),
    ]


def elapse_periodic_with_cooldown(
    state: _StateT,
    time: float,
    periodic_damage: float,
    periodic_hit: float,
) -> tuple[_StateT, list[Event]]:
    """
    elapse_periodic_damage_trait
    """
    cooldown, periodic = (
        state["cooldown"].model_copy(),
        state["periodic"].model_copy(),
    )

    cooldown.elapse(time)
    lapse_count = periodic.elapse(time)

    state["cooldown"] = cooldown
    state["periodic"] = periodic

    return state, [EmptyEvent.elapsed(time)] + [
        EmptyEvent.dealt(periodic_damage, periodic_hit) for _ in range(lapse_count)
    ]


class _PeriodicOnlyState(TypedDict):
    periodic: Periodic
    dynamics: Dynamics


def running_view(
    state: _PeriodicOnlyState,
    id: str,
    name: str,
    lasting_duration: float,
) -> Running:
    return Running(
        id=id,
        name=name,
        time_left=state["periodic"].time_left,
        lasting_duration=lasting_duration,
    )
