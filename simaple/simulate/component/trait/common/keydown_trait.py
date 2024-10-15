from typing import TypedDict, TypeVar

from simaple.simulate.component.entity import Cooldown, Keydown
from simaple.simulate.component.view import KeydownView, Running, Validity
from simaple.simulate.core import Event
from simaple.simulate.event import EmptyEvent
from simaple.simulate.global_property import Dynamics


class _State(TypedDict):
    cooldown: Cooldown
    keydown: Keydown
    dynamics: Dynamics


_StateT = TypeVar("_StateT", bound=_State)


def use_keydown(
    state: _StateT,
    maximum_keydown_time: float,
    keydown_prepare_delay: float,
    cooldown_duration: float,
) -> tuple[_StateT, list[Event]]:
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


def elapse_keydown(
    state: _StateT,
    time: float,
    damage: float,
    hit: float,
    finish_damage: float,
    finish_hit: float,
    finish_delay: float,
) -> tuple[_StateT, list[Event]]:
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


def stop_keydown(
    state: _StateT,
    finish_damage: float,
    finish_hit: float,
    finish_delay: float,
) -> tuple[_StateT, list[Event]]:
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


def keydown_view(state: _State, name: str) -> KeydownView:
    return KeydownView(
        name=name,
        time_left=state["keydown"].time_left,
        running=state["keydown"].running,
    )
