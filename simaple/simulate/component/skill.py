from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.component.base import (
    Component,
    ReducerState,
    reducer_method,
    view_method,
)
from simaple.simulate.component.entity import (
    Consumable,
    Cooldown,
    Lasting,
    Periodic,
    Stack,
)
from simaple.simulate.component.trait.impl import (
    AddDOTDamageTrait,
    BuffTrait,
    ConsumableBuffTrait,
    ConsumableValidityTrait,
    CooldownValidityTrait,
    InvalidatableCooldownTrait,
    PeriodicWithSimpleDamageTrait,
    UsePeriodicDamageTrait,
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


class MultipleAttackSkillState(ReducerState):
    cooldown: Cooldown
    dynamics: Dynamics


class MultipleAttackSkillComponent(
    SkillComponent, InvalidatableCooldownTrait, UseSimpleAttackTrait
):
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    multiple: int

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, state: MultipleAttackSkillState):
        return self.elapse_simple_attack(time, state)

    @reducer_method
    def use(self, _: None, state: MultipleAttackSkillState):
        return self.use_multiple_damage(state, self.multiple)

    @reducer_method
    def reset_cooldown(self, _: None, state: MultipleAttackSkillState):
        state = state.deepcopy()
        state.cooldown.set_time_left(0)
        return state, None

    @view_method
    def validity(self, state: MultipleAttackSkillState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit


class DOTEmittingState(ReducerState):
    cooldown: Cooldown
    dynamics: Dynamics


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
    def elapse(self, time: float, state: DOTEmittingState):
        return self.elapse_simple_attack(time, state)

    @reducer_method
    def use(self, _: None, state: DOTEmittingState):
        state, event = self.use_simple_attack(state)
        event += [self.get_dot_add_event()]
        return state, event

    @reducer_method
    def reset_cooldown(self, _: None, state: DOTEmittingState):
        state = state.deepcopy()
        state.cooldown.set_time_left(0)
        return state, None

    @view_method
    def validity(self, state: DOTEmittingState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit

    def _get_dot_damage_and_lasting(self) -> tuple[float, float]:
        return self.dot_damage, self.dot_lasting_duration


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


class NoState(ReducerState):
    ...


class AlwaysEnabledComponent(Component):
    stat: Stat

    def get_default_state(self):
        return {}

    @view_method
    def buff(self, _: NoState) -> Optional[Stat]:
        return self.stat

    @view_method
    def running(self, _: NoState) -> Running:
        return Running(
            name=self.name, time_left=999_999_999, lasting_duration=999_999_999
        )


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


class ConsumableBuffSkillState(ReducerState):
    consumable: Consumable
    lasting: Lasting
    dynamics: Dynamics


class ConsumableBuffSkillComponent(
    SkillComponent, ConsumableBuffTrait, ConsumableValidityTrait
):
    stat: Stat
    cooldown_duration: float
    delay: float
    lasting_duration: float
    maximum_stack: int
    # TODO: use rem argument to apply buff remnance

    def get_default_state(self):
        return {
            "consumable": Consumable(
                time_left=self.cooldown_duration,
                cooldown_duration=self.cooldown_duration,
                maximum_stack=self.maximum_stack,
                stack=self.maximum_stack,
            ),
            "lasting": Lasting(time_left=0),
        }

    @reducer_method
    def use(self, _: None, state: ConsumableBuffSkillState):
        return self.use_consumable_buff_trait(state)

    @reducer_method
    def elapse(self, time: float, state: ConsumableBuffSkillState):
        return self.elapse_consumable_buff_trait(time, state)

    @view_method
    def validity(self, state: ConsumableBuffSkillState):
        return self.validity_in_consumable_trait(state)

    @view_method
    def buff(self, state: ConsumableBuffSkillState) -> Optional[Stat]:
        if state.lasting.enabled():
            return self.stat

        return None

    @view_method
    def running(self, state: ConsumableBuffSkillState) -> Running:
        return Running(
            name=self.name,
            time_left=state.lasting.time_left,
            lasting_duration=self._get_lasting_duration(state),
        )

    def _get_lasting_duration(self, state) -> float:
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


class HitLimitedPeriodicDamageState(ReducerState):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class HitLimitedPeriodicDamageComponent(
    SkillComponent, UsePeriodicDamageTrait, CooldownValidityTrait
):
    name: str
    cooldown_duration: float
    delay: float

    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float

    max_count: int

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(interval=self.periodic_interval, time_left=0),
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        state: HitLimitedPeriodicDamageState,
    ):
        state = state.deepcopy()

        state.cooldown.elapse(time)
        dealing_events = []

        for _ in state.periodic.resolving(time):
            if state.periodic.count >= self.max_count:
                break

            dealing_events.append(
                self.event_provider.dealt(
                    self.periodic_damage,
                    self.periodic_hit,
                )
            )

        if state.periodic.count >= self.max_count:
            state.periodic.disable()

        return state, [self.event_provider.elapsed(time)] + dealing_events

    @reducer_method
    def use(self, _: None, state: HitLimitedPeriodicDamageState):
        return self.use_periodic_damage_trait(state)

    @view_method
    def validity(self, state: HitLimitedPeriodicDamageState):
        return self.validity_in_cooldown_trait(state)

    def _get_lasting_duration(self, state: HitLimitedPeriodicDamageState) -> float:
        return self.lasting_duration
