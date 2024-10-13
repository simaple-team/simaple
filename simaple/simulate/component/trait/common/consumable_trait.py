from typing import TypedDict, TypeVar

from simaple.simulate.component.entity import Consumable, Cooldown, Lasting
from simaple.simulate.component.view import KeydownView, Running, Validity
from simaple.simulate.core import Event
from simaple.simulate.event import EmptyEvent
from simaple.simulate.global_property import Dynamics


class _State(TypedDict):
    consumable: Consumable
    lasting: Lasting
    dynamics: Dynamics


_StateT = TypeVar("_StateT", bound=_State)


def start_consumable_buff(
    state: _StateT, lasting_duration: float, delay: float, apply_buff_duration: bool
) -> tuple[_StateT, list[Event]]:
    consumable, lasting = (
        state["consumable"].model_copy(),
        state["lasting"].model_copy(),
    )

    if not consumable.available:
        return state, [EmptyEvent.rejected()]

    consumable.consume()

    lasting.set_time_left(
        state["dynamics"].stat.calculate_buff_duration(lasting_duration)
        if apply_buff_duration
        else lasting_duration
    )

    state["consumable"] = consumable
    state["lasting"] = lasting

    return state, [EmptyEvent.delayed(delay)]


def elapse_consumable_buff(
    state: _StateT,
    time: float,
) -> tuple[_StateT, list[Event]]:
    consumable, lasting = (
        state["consumable"].model_copy(),
        state["lasting"].model_copy(),
    )

    consumable.elapse(time)
    lasting.elapse(time)

    state["consumable"] = consumable
    state["lasting"] = lasting

    return state, [EmptyEvent.elapsed(time)]


def consumable_validity(
    state: _State, id: str, name: str, cooldown_duration: float
) -> Validity:
    return Validity(
        id=id,
        name=name,
        time_left=max(0, state["consumable"].time_left),
        valid=state["consumable"].available,
        cooldown_duration=cooldown_duration,
        stack=state["consumable"].stack,
    )
