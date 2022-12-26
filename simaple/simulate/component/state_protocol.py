from typing import Protocol, TypeVar

from simaple.simulate.component.entity import Cooldown, Duration, Periodic
from simaple.simulate.global_property import Dynamics

T = TypeVar("T")


class CopyProtocol(Protocol[T]):
    def copy(self: T) -> T:
        pass


class CooldownProtocol(CopyProtocol, Protocol):
    cooldown: Cooldown


CooldownGeneric = TypeVar("CooldownGeneric", bound=CooldownProtocol)


class DurationProtocol(CopyProtocol, Protocol):
    duration: Duration


DurationGeneric = TypeVar("DurationGeneric", bound=DurationProtocol)


class PeriodicProtocol(CopyProtocol, Protocol):
    periodic: Periodic


PeriodicGeneric = TypeVar("PeriodicGeneric", bound=PeriodicProtocol)


class DynamicsProtocol(CopyProtocol, Protocol):
    dynamics: Dynamics


DynamicsGeneric = TypeVar("DynamicsGeneric", bound=DynamicsProtocol)


class CooldownDurationDynamicsProtocol(
    CooldownProtocol, DurationProtocol, DynamicsProtocol, Protocol
):
    pass


CooldownDurationDynamicsGeneric = TypeVar(
    "CooldownDurationDynamicsGeneric", bound=CooldownDurationDynamicsProtocol
)


class CooldownDynamicsProtocol(DynamicsProtocol, CooldownProtocol, Protocol):
    pass


CooldownDynamicsGeneric = TypeVar(
    "CooldownDynamicsGeneric", bound=CooldownDynamicsProtocol
)


class CooldownPeriodicProtocol(CooldownProtocol, PeriodicProtocol, Protocol):
    pass


CooldownPeriodicGeneric = TypeVar(
    "CooldownPeriodicGeneric", bound=CooldownPeriodicProtocol
)


class CooldownDynamicsPeriodicProtocol(
    CooldownProtocol, PeriodicProtocol, DynamicsProtocol, Protocol
):
    pass


CooldownDynamicsPeriodicGeneric = TypeVar(
    "CooldownDynamicsPeriodicGeneric", bound=CooldownDynamicsPeriodicProtocol
)
