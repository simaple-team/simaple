from typing import TypedDict, TypeVar

from typing_extensions import Unpack

from simaple.simulate.component.entity import Cooldown, Periodic
from simaple.simulate.component.view import Running
from simaple.simulate.core import ElapseActionPayload, Event, UseActionPayload
from simaple.simulate.event import EmptyEvent
from simaple.simulate.global_property import Dynamics


class _State(TypedDict):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


_StateT = TypeVar("_StateT", bound=_State)


class StartPeriodicWithCooldownProps(TypedDict):
    damage: float
    hit: float
    delay: float
    cooldown_duration: float
    lasting_duration: float


def start_periodic_with_cooldown(
    state: _StateT,
    _payload: UseActionPayload,
    **props: Unpack[StartPeriodicWithCooldownProps],
) -> tuple[_StateT, list[Event]]:
    """use_periodic_damage_trait"""
    damage, hit, delay, cooldown_duration, lasting_duration = (
        props["damage"],
        props["hit"],
        props["delay"],
        props["cooldown_duration"],
        props["lasting_duration"],
    )

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


class ElapsePeriodicWithCooldownProps(TypedDict):
    periodic_damage: float
    periodic_hit: float


def elapse_periodic_with_cooldown(
    state: _StateT,
    payload: ElapseActionPayload,
    **props: Unpack[ElapsePeriodicWithCooldownProps],
) -> tuple[_StateT, list[Event]]:
    """
    elapse_periodic_damage_trait
    """
    time = payload["time"]
    periodic_damage, periodic_hit = (
        props["periodic_damage"],
        props["periodic_hit"],
    )
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


class PeriodicValidityProps(TypedDict):
    id: str
    name: str
    lasting_duration: float


def running_view(
    state: _PeriodicOnlyState,
    **props: Unpack[PeriodicValidityProps],
) -> Running:
    return Running(
        id=props["id"],
        name=props["name"],
        time_left=state["periodic"].time_left,
        lasting_duration=props["lasting_duration"],
    )
