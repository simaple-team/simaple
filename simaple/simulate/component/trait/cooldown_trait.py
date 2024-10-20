from typing import Any, TypedDict, TypeVar

from typing_extensions import Unpack

from simaple.simulate.component.entity import Cooldown
from simaple.simulate.component.view import Validity
from simaple.simulate.core import Event
from simaple.simulate.core.action import ElapseActionPayload
from simaple.simulate.event import EmptyEvent


class _State(TypedDict):
    cooldown: Cooldown


StateT = TypeVar("StateT", bound=_State)


def reset_cooldown(state: StateT, _: Any) -> tuple[StateT, list[Event]]:
    cooldown = state["cooldown"].model_copy()
    cooldown.set_time_left(0)

    state["cooldown"] = cooldown

    return state, []


def elapse_cooldown_only(
    state: StateT, props: ElapseActionPayload
) -> tuple[StateT, list[Event]]:
    time = props["time"]

    cooldown = state["cooldown"].model_copy()
    cooldown.elapse(time)

    state["cooldown"] = cooldown

    return state, [EmptyEvent.elapsed(time)]


class ValidityViewProps(TypedDict):
    id: str
    name: str
    cooldown_duration: float


def validity_view(state: _State, **props: Unpack[ValidityViewProps]) -> Validity:
    """
    Renewal for `validity_in_invalidatable_cooldown_trait`.
    """
    id, name, cooldown_duration = (
        props["id"],
        props["name"],
        props["cooldown_duration"],
    )

    return Validity(
        id=id,
        name=name,
        time_left=state["cooldown"].minimum_time_to_available(),
        valid=state["cooldown"].available,
        cooldown_duration=cooldown_duration,
    )
