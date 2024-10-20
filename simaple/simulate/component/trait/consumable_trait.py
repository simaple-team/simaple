from typing import TypedDict, TypeVar

from typing_extensions import Unpack

from simaple.simulate.component.entity import Consumable, Lasting
from simaple.simulate.component.view import Validity
from simaple.simulate.core import ElapseActionPayload, Event, UseActionPayload
from simaple.simulate.event import EmptyEvent
from simaple.simulate.global_property import Dynamics


class _State(TypedDict):
    consumable: Consumable
    lasting: Lasting
    dynamics: Dynamics


_StateT = TypeVar("_StateT", bound=_State)


class StartConsumableBuffProps(TypedDict):
    lasting_duration: float
    delay: float
    apply_buff_duration: bool


def start_consumable_buff(
    state: _StateT,
    _: UseActionPayload,
    **props: Unpack[StartConsumableBuffProps],
) -> tuple[_StateT, list[Event]]:
    lasting_duration, delay, apply_buff_duration = (
        props["lasting_duration"],
        props["delay"],
        props["apply_buff_duration"],
    )

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
    payload: ElapseActionPayload,
) -> tuple[_StateT, list[Event]]:
    time = payload["time"]

    consumable, lasting = (
        state["consumable"].model_copy(),
        state["lasting"].model_copy(),
    )

    consumable.elapse(time)
    lasting.elapse(time)

    state["consumable"] = consumable
    state["lasting"] = lasting

    return state, [EmptyEvent.elapsed(time)]


class _StateWithoutLasting(TypedDict):
    consumable: Consumable
    dynamics: Dynamics


class ConsumableValidityProps(TypedDict):
    id: str
    name: str
    cooldown_duration: float


def consumable_validity(
    state: _StateWithoutLasting, **props: Unpack[ConsumableValidityProps]
) -> Validity:
    return Validity(
        id=props["id"],
        name=props["name"],
        time_left=max(0, state["consumable"].time_left),
        valid=state["consumable"].available,
        cooldown_duration=props["cooldown_duration"],
        stack=state["consumable"].stack,
    )
