from simaple.simulate.base import Entity
from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import CooldownState, IntervalState, StackState
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import (
    CooldownValidityTrait,
    TickEmittingTrait,
)
from simaple.simulate.component.util import is_rejected
from simaple.simulate.component.view import Running, Validity
from simaple.simulate.global_property import Dynamics


class PoisonNovaEntity(Entity):
    time_left: float
    maximum_time_left: float

    def create_nova(self, remaining_time):
        self.time_left = remaining_time

    def try_trigger_nova(self) -> bool:
        if 0 < self.time_left < self.maximum_time_left:
            self.time_left = 0
            return True

        return False

    def elapse(self, time: float):
        self.time_left -= time


class PoisonNovaState(ReducerState):
    cooldown_state: CooldownState
    poison_nova: PoisonNovaEntity
    dynamics: Dynamics


class PoisonNovaComponent(SkillComponent):
    name: str
    damage: float
    hit: float

    nova_remaining_time: float = 4000
    nova_damage: float
    nova_single_hit: int
    nova_hit_count: int

    listening_actions: dict[str, str] = {"미스트 이럽션.use": "trigger"}

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
            "poison_nova": PoisonNovaEntity(
                time_left=0, maximum_time_left=100 * 1000.0
            ),
        }

    @reducer_method
    def elapse(self, time: float, state: PoisonNovaState):
        state = state.copy()
        state.cooldown_state.elapse(time)
        state.poison_nova.elapse(time)
        return state, self.event_provider.elapsed(time)

    @reducer_method
    def use(self, _: None, state: PoisonNovaState):
        state = state.copy()

        if not state.cooldown_state.available:
            return state, self.event_provider.rejected()

        state.cooldown_state.set_time_left(
            state.dynamics.stat.calculate_cooldown(self.cooldown)
        )
        state.poison_nova.create_nova(self.nova_remaining_time)

        return state, [
            self.event_provider.dealt(self.damage, self.hit),
            self.event_provider.delayed(self.delay),
        ]

    @reducer_method
    def trigger(self, _: None, state: PoisonNovaState):
        state = state.copy()

        triggered = state.poison_nova.try_trigger_nova()
        if triggered:
            return state, [
                self.event_provider.dealt(
                    self.nova_damage, self.nova_single_hit * min(self.nova_hit_count, 3)
                ),
                self.event_provider.dealt(
                    self.nova_damage * 0.5,
                    self.nova_single_hit * max(self.nova_hit_count - 3, 0),
                ),
            ]

        return state, None

    @view_method
    def validity(self, state: PoisonNovaState):
        return Validity(
            name=self.name,
            time_left=max(0, state.cooldown_state.time_left),
            valid=state.cooldown_state.available,
            cooldown=self.cooldown,
        )


class PoisonChainState(ReducerState):
    cooldown_state: CooldownState
    interval_state: IntervalState
    stack_state: StackState
    dynamics: Dynamics


class PoisonChainComponent(SkillComponent, TickEmittingTrait, CooldownValidityTrait):
    name: str
    damage: float
    hit: float
    cooldown: float
    delay: float

    tick_interval: float
    tick_damage: float
    tick_hit: float
    duration: float

    tick_damage_increment: float

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
            "interval_state": IntervalState(interval=self.tick_interval, time_left=0),
            "stack_state": StackState(maximum_stack=5),
        }

    def get_tick_damage(self, state: PoisonChainState):
        return (
            self.tick_damage
            + self.tick_damage_increment * state.stack_state.get_stack()
        )

    @reducer_method
    def elapse(self, time: float, state: PoisonChainState):
        state = state.copy()

        state.cooldown_state.elapse(time)

        dealing_events = []

        for _ in state.interval_state.resolving(time):
            dealing_events.append(
                self.event_provider.dealt(self.get_tick_damage(state), self.tick_hit)
            )
            state.stack_state.increase(1)

        return state, [self.event_provider.elapsed(time)] + dealing_events

    @reducer_method
    def use(self, _: None, state: PoisonChainState):
        state = state.copy()

        state, events = self.use_tick_emitting_trait(state)
        if not is_rejected(events):
            state.stack_state.reset(1)

        return state, events

    @view_method
    def validity(self, state: PoisonChainState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def running(self, state: PoisonChainState) -> Running:
        return Running(
            name=self.name,
            time_left=state.interval_state.interval_time_left,
            duration=self._get_duration(state),
        )

    def _get_duration(self, state: PoisonChainState) -> float:
        return self.duration

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit

    def _get_tick_damage_hit(self, state: PoisonChainState) -> tuple[float, float]:
        return self.tick_damage, self.tick_hit
