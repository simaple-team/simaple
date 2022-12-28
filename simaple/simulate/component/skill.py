from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.component.base import (
    Component,
    ReducerState,
    reducer_method,
    view_method,
)
from simaple.simulate.component.entity import Cooldown, Lasting, Periodic, Stack
from simaple.simulate.component.trait.impl import (
    AddDOTDamageTrait,
    BuffTrait,
    InvalidatableCooldownTrait,
    PeriodicWithSimpleDamageTrait,
    UseSimpleAttackTrait,
)
from simaple.simulate.component.view import Running, Validity
from simaple.simulate.event import EventProvider, NamedEventProvider
from simaple.simulate.global_property import Dynamics


class SkillComponent(Component):
    disable_validity: bool = False
    modifier: Optional[Stat]
    cooldown_duration: float
    delay: float

    @property
    def event_provider(self) -> EventProvider:
        return NamedEventProvider(self.name, self.modifier)

    def invalidate_if_disabled(self, validity: Validity):
        if self.disable_validity:
            validity = validity.copy()
            validity.valid = False
            return validity

        return validity

    def _get_cooldown_duration(self) -> float:
        return self.cooldown_duration

    def _get_delay(self) -> float:
        return self.delay

    def _get_name(self) -> str:
        return self.name


class AttackSkillState(ReducerState):
    cooldown: Cooldown
    dynamics: Dynamics


class AttackSkillComponent(
    SkillComponent, InvalidatableCooldownTrait, UseSimpleAttackTrait
):
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, state: AttackSkillState):
        return self.elapse_simple_attack(time, state)

    @reducer_method
    def use(self, _: None, state: AttackSkillState):
        return self.use_simple_attack(state)

    @reducer_method
    def reset_cooldown(self, _: None, state: AttackSkillState):
        state = state.deepcopy()
        state.cooldown.set_time_left(0)
        return state, None

    @view_method
    def validity(self, state: AttackSkillState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit


class DOTEmittingAttackSkillComponent(
    SkillComponent, InvalidatableCooldownTrait, UseSimpleAttackTrait, AddDOTDamageTrait
):
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    dot_damage: float
    dot_lasting_duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, state: AttackSkillState):
        return self.elapse_simple_attack(time, state)

    @reducer_method
    def use(self, _: None, state: AttackSkillState):
        state, event = self.use_simple_attack(state)
        event += [self.get_dot_add_event()]
        return state, event

    @reducer_method
    def reset_cooldown(self, _: None, state: AttackSkillState):
        state = state.copy()
        state.cooldown.set_time_left(0)
        return state, None

    @view_method
    def validity(self, state: AttackSkillState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit

    def _get_dot_damage_and_lasting(self) -> tuple[float, float]:
        return self.dot_damage, self.dot_lasting_duration


class MultipleAttackSkillComponent(AttackSkillComponent):
    multiple: int

    @reducer_method
    def use(self, _: None, state: AttackSkillState):
        state = state.deepcopy()

        if not state.cooldown.available:
            return state, self.event_provider.rejected()

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self.cooldown_duration)
        )

        return state, [
            self.event_provider.dealt(self.damage, self.hit)
            for _ in range(self.multiple)
        ] + [self.event_provider.delayed(self.delay)]


class BuffSkillState(ReducerState):
    cooldown: Cooldown
    lasting: Lasting
    dynamics: Dynamics


class BuffSkillComponent(SkillComponent, BuffTrait, InvalidatableCooldownTrait):
    stat: Stat
    cooldown_duration: float
    delay: float
    lasting_duration: float
    # TODO: use rem, red argument to apply cooltime reduction and buff remnance

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
        }

    @reducer_method
    def use(self, _: None, state: BuffSkillState):
        return self.use_buff_trait(state)

    @reducer_method
    def elapse(self, time: float, state: BuffSkillState):
        return self.elapse_buff_trait(time, state)

    @view_method
    def validity(self, state: BuffSkillState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    @view_method
    def buff(self, state: BuffSkillState) -> Optional[Stat]:
        if state.lasting.enabled():
            return self.stat

        return None

    @view_method
    def running(self, state: BuffSkillState) -> Running:
        return self.running_in_buff_trait(state)

    def _get_lasting_duration(self, state: BuffSkillState) -> float:
        return self.lasting_duration


class StackableBuffSkillState(ReducerState):
    cooldown: Cooldown
    lasting: Lasting
    stack: Stack
    dynamics: Dynamics


class StackableBuffSkillComponent(
    SkillComponent, BuffTrait, InvalidatableCooldownTrait
):
    stat: Stat
    cooldown_duration: float
    delay: float
    lasting_duration: float
    maximum_stack: int
    # TODO: use rem, red argument to apply cooltime reduction and buff remnance

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
            "stack": Stack(maximum_stack=self.maximum_stack),
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: StackableBuffSkillState,
    ):
        state = state.deepcopy()
        if state.lasting.time_left <= 0:
            state.stack.reset()
        state.stack.increase()

        return self.use_buff_trait(state)

    @reducer_method
    def elapse(
        self,
        time: float,
        state: StackableBuffSkillState,
    ):
        return self.elapse_buff_trait(time, state)

    @view_method
    def validity(self, state: StackableBuffSkillState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    @view_method
    def buff(self, state: StackableBuffSkillState) -> Optional[Stat]:
        if state.lasting.enabled():
            return self.stat.stack(state.stack.stack)

        return None

    @view_method
    def running(self, state: StackableBuffSkillState) -> Running:
        return Running(
            name=self.name,
            time_left=state.lasting.time_left,
            lasting_duration=self._get_lasting_duration(state),
            stack=state.stack.stack if state.lasting.time_left > 0 else 0,
        )

    def _get_lasting_duration(self, state: StackableBuffSkillState) -> float:
        return self.lasting_duration


class PeriodicDamageState(ReducerState):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class PeriodicDamageConfiguratedAttackSkillComponent(
    SkillComponent, PeriodicWithSimpleDamageTrait, InvalidatableCooldownTrait
):
    name: str
    damage: float
    hit: float
    delay: float

    cooldown_duration: float

    periodic_interval: float
    periodic_damage: float
    periodic_hit: float

    lasting_duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(interval=self.periodic_interval, time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, state: PeriodicDamageState):
        return self.elapse_periodic_damage_trait(time, state)

    @reducer_method
    def use(self, _: None, state: PeriodicDamageState):
        return self.use_periodic_damage_trait(state)

    @view_method
    def validity(self, state: PeriodicDamageState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    @view_method
    def running(self, state: PeriodicDamageState) -> Running:
        return Running(
            name=self.name,
            time_left=state.periodic.time_left,
            lasting_duration=self._get_lasting_duration(state),
        )

    def _get_lasting_duration(self, state: PeriodicDamageState) -> float:
        return self.lasting_duration

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit

    def _get_periodic_damage_hit(
        self, state: PeriodicDamageState
    ) -> tuple[float, float]:
        return self.periodic_damage, self.periodic_hit
