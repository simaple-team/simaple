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


class LastingTrait(ComponentTrait):
    @abstractmethod
    def _get_lasting_duration(self, state) -> float:
        ...


class KeydownTrait(ComponentTrait):
    @abstractmethod
    def _get_maximum_keydown_time_prepare_delay(self) -> tuple[float, float]:
        ...

    @abstractmethod
    def _get_keydown_damage_hit(self) -> tuple[float, float]:
        ...

    @abstractmethod
    def _get_keydown_end_damage_hit_delay(self) -> tuple[float, float, float]:
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


class PeriodicDamageTrait(ComponentTrait):
    @abstractmethod
    def _get_periodic_damage_hit(self, state) -> tuple[float, float]:
        ...


class DOTTrait(ComponentTrait):
    @abstractmethod
    def _get_dot_damage_and_lasting(self) -> tuple[float, float]:
        ...
