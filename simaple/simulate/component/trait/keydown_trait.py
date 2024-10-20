from typing import TypedDict, TypeVar

from typing_extensions import Unpack

from simaple.simulate.component.entity import Cooldown, Keydown
from simaple.simulate.component.view import KeydownView
from simaple.simulate.core import (
    ElapseActionPayload,
    Event,
    StopActionPayload,
    UseActionPayload,
)
from simaple.simulate.event import EmptyEvent
from simaple.simulate.global_property import Dynamics


class _State(TypedDict):
    cooldown: Cooldown
    keydown: Keydown
    dynamics: Dynamics


_StateT = TypeVar("_StateT", bound=_State)


class UseKeydownProps(TypedDict):
    maximum_keydown_time: float
    keydown_prepare_delay: float
    cooldown_duration: float


def use_keydown(
    state: _StateT,
    _payload: UseActionPayload,
    **props: Unpack[UseKeydownProps],
) -> tuple[_StateT, list[Event]]:
    maximum_keydown_time, keydown_prepare_delay, cooldown_duration = (
        props["maximum_keydown_time"],
        props["keydown_prepare_delay"],
        props["cooldown_duration"],
    )

    if not state["cooldown"].available or state["keydown"].running:
        return state, [EmptyEvent.rejected()]

    keydown, cooldown = (
        state["keydown"].model_copy(),
        state["cooldown"].model_copy(),
    )

    cooldown.set_time_left(state["dynamics"].stat.calculate_cooldown(cooldown_duration))
    keydown.start(maximum_keydown_time, keydown_prepare_delay)

    state["keydown"] = keydown
    state["cooldown"] = cooldown

    return state, [EmptyEvent.delayed(keydown_prepare_delay)]


class ElapseKeydownProps(TypedDict):
    damage: float
    hit: float
    finish_damage: float
    finish_hit: float
    finish_delay: float


def elapse_keydown(
    state: _StateT,
    payload: ElapseActionPayload,
    **props: Unpack[ElapseKeydownProps],
) -> tuple[_StateT, list[Event]]:
    time = payload["time"]
    damage, hit, finish_damage, finish_hit, finish_delay = (
        props["damage"],
        props["hit"],
        props["finish_damage"],
        props["finish_hit"],
        props["finish_delay"],
    )

    keydown, cooldown = (
        state["keydown"].model_copy(),
        state["cooldown"].model_copy(),
    )
    cooldown.elapse(time)

    damage_hits: list[tuple[float, float]] = []

    was_running = keydown.running
    for _ in keydown.resolving(time):
        damage_hits += [(damage, hit)]

    keydown_end = was_running and not keydown.running
    if keydown_end:
        damage_hits += [(finish_damage, finish_hit)]
        # time_left is negative value here, represents time exceeded after actual keydown end.
        delay = max(finish_delay + keydown.time_left, 0)
    else:
        delay = keydown.get_next_delay()

    state["keydown"] = keydown
    state["cooldown"] = cooldown

    return (
        state,
        [EmptyEvent.dealt(damage, hit) for damage, hit in damage_hits]
        + [EmptyEvent.delayed(delay), EmptyEvent.elapsed(time)]
        + ([EmptyEvent.keydown_end()] if keydown_end else []),
    )


class StopKeydownProps(TypedDict):
    finish_damage: float
    finish_hit: float
    finish_delay: float


def stop_keydown(
    state: _StateT,
    _: StopActionPayload,
    **props: Unpack[StopKeydownProps],
) -> tuple[_StateT, list[Event]]:
    finish_damage, finish_hit, finish_delay = (
        props["finish_damage"],
        props["finish_hit"],
        props["finish_delay"],
    )

    keydown = state["keydown"].model_copy()

    if not keydown.running:
        return state, [EmptyEvent.rejected()]

    keydown.stop()

    state["keydown"] = keydown

    return (
        state,
        [
            EmptyEvent.dealt(finish_damage, finish_hit),
            EmptyEvent.delayed(finish_delay),
            EmptyEvent.keydown_end(),
        ],
    )


class ValidityViewProps(TypedDict):
    name: str


def keydown_view(state: _State, **props: Unpack[ValidityViewProps]) -> KeydownView:
    return KeydownView(
        name=props["name"],
        time_left=state["keydown"].time_left,
        running=state["keydown"].running,
    )
