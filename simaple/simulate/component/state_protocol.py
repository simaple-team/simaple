from typing import Protocol, TypeVar

from simaple.simulate.component.entity import (
    Consumable,
    Cooldown,
    Keydown,
    Lasting,
    Periodic,
)
from simaple.simulate.global_property import Dynamics

T = TypeVar("T")


class DeepcopyProtocol(Protocol[T]):
    def deepcopy(self: T) -> T:
        pass


class CooldownProtocol(DeepcopyProtocol, Protocol):
    cooldown: Cooldown


CooldownGeneric = TypeVar("CooldownGeneric", bound=CooldownProtocol)


class ConsumableProtocol(DeepcopyProtocol, Protocol):
    consumable: Consumable


ConsumableGeneric = TypeVar("ConsumableGeneric", bound=ConsumableProtocol)


class LastingProtocol(DeepcopyProtocol, Protocol):
    lasting: Lasting


LastingGeneric = TypeVar("LastingGeneric", bound=LastingProtocol)


class PeriodicProtocol(DeepcopyProtocol, Protocol):
    periodic: Periodic


PeriodicGeneric = TypeVar("PeriodicGeneric", bound=PeriodicProtocol)


class KeydownProtocol(DeepcopyProtocol, Protocol):
    keydown: Keydown


KeydownGeneric = TypeVar("KeydownGeneric", bound=KeydownProtocol)


class DynamicsProtocol(DeepcopyProtocol, Protocol):
    dynamics: Dynamics


DynamicsGeneric = TypeVar("DynamicsGeneric", bound=DynamicsProtocol)


class ConsumableDynamicsLastingProtocol(
    ConsumableProtocol, DynamicsProtocol, LastingProtocol, Protocol
):
    pass


ConsumableDynamicsLastingGeneric = TypeVar(
    "ConsumableDynamicsLastingGeneric", bound=ConsumableDynamicsLastingProtocol
)


class CooldownDynamicsLastingProtocol(
    CooldownProtocol, DynamicsProtocol, LastingProtocol, Protocol
):
    pass


CooldownDynamicsLastingGeneric = TypeVar(
    "CooldownDynamicsLastingGeneric", bound=CooldownDynamicsLastingProtocol
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


class CooldownDynamicsKeydownProtocol(
    CooldownProtocol, KeydownProtocol, DynamicsProtocol, Protocol
):
    pass


CooldownDynamicsKeydownGeneric = TypeVar(
    "CooldownDynamicsKeydownGeneric", bound=CooldownDynamicsKeydownProtocol
)
