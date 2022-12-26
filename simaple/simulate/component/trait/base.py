from abc import ABCMeta, abstractmethod

from simaple.simulate.component.view import Validity
from simaple.simulate.event import EventProvider


class ComponentTrait(metaclass=ABCMeta):
    ...


class EventProviderTrait(ComponentTrait):
    @property
    @abstractmethod
    def event_provider(self) -> EventProvider:
        ...


class CooldownTrait(ComponentTrait):
    @abstractmethod
    def _get_cooldown_duration(self) -> float:
        ...


class DelayTrait(ComponentTrait):
    @abstractmethod
    def _get_delay(self) -> float:
        ...


class DurationTrait(ComponentTrait):
    @abstractmethod
    def _get_lasting_duration(self, state) -> float:
        ...


class SimpleDamageTrait(ComponentTrait):
    @abstractmethod
    def _get_simple_damage_hit(self) -> tuple[float, float]:
        ...


class NamedTrait(ComponentTrait):
    @abstractmethod
    def _get_name(self) -> str:
        ...


class InvalidatableTrait(ComponentTrait):
    @abstractmethod
    def invalidate_if_disabled(self, validity: Validity) -> Validity:
        ...


class TickDamageTrait(ComponentTrait):
    @abstractmethod
    def _get_tick_damage_hit(self, state) -> tuple[float, float]:
        ...
