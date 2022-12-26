from typing import Protocol, TypeVar

from simaple.simulate.component.state_fragment import (
    CooldownState,
    DurationState,
    IntervalState,
)
from simaple.simulate.global_property import Dynamics

T = TypeVar("T")


class CopyProtocol(Protocol[T]):
    def copy(self: T) -> T:
        pass


class CooldownProtocol(CopyProtocol, Protocol):
    cooldown_state: CooldownState


class DurationProtocol(CopyProtocol, Protocol):
    duration_state: DurationState


class IntervalProtocol(CopyProtocol, Protocol):
    interval_state: IntervalState


class DynamicsProtocol(CopyProtocol, Protocol):
    dynamics: Dynamics


class CooldownDurationDynamicsProtocol(
    CooldownProtocol, DurationProtocol, DynamicsProtocol, Protocol
):
    pass


class CooldownDynamicsProtocol(DynamicsProtocol, CooldownProtocol, Protocol):
    pass


class CooldownIntervalProtocol(CooldownProtocol, IntervalProtocol, Protocol):
    pass


class CooldownDynamicsIntervalProtocol(
    CooldownProtocol, IntervalProtocol, DynamicsProtocol, Protocol
):
    pass
