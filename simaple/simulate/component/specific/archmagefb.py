from simaple.simulate.base import State
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.state import CooldownState, IntervalState, StackState
from simaple.simulate.component.trait.impl import (
    CooldownValidityTrait,
    TickEmittingTrait,
)
from simaple.simulate.component.util import is_rejected
from simaple.simulate.component.view import Running, Validity
from simaple.simulate.global_property import Dynamics


class PoisonNovaState(State):
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
            "nova_state": PoisonNovaState(time_left=0, maximum_time_left=100 * 1000.0),
        }

    @reducer_method
    def elapse(
        self, time: float, cooldown_state: CooldownState, nova_state: PoisonNovaState
    ):
        cooldown_state, nova_state = cooldown_state.copy(), nova_state.copy()
        cooldown_state.elapse(time)
        nova_state.elapse(time)
        return (cooldown_state, nova_state), self.event_provider.elapsed(time)

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        nova_state: PoisonNovaState,
        dynamics: Dynamics,
    ):
        cooldown_state, nova_state = cooldown_state.copy(), nova_state.copy()

        if not cooldown_state.available:
            return (
                cooldown_state,
                nova_state,
                dynamics,
            ), self.event_provider.rejected()

        cooldown_state.set_time_left(dynamics.stat.calculate_cooldown(self.cooldown))
        nova_state.create_nova(self.nova_remaining_time)

        return (cooldown_state, nova_state, dynamics), [
            self.event_provider.dealt(self.damage, self.hit),
            self.event_provider.delayed(self.delay),
        ]

    @reducer_method
    def trigger(self, _: None, nova_state: PoisonNovaState):
        nova_state = nova_state.copy()
        triggered = nova_state.try_trigger_nova()
        if triggered:
            return nova_state, [
                self.event_provider.dealt(
                    self.nova_damage, self.nova_single_hit * min(self.nova_hit_count, 3)
                ),
                self.event_provider.dealt(
                    self.nova_damage * 0.5,
                    self.nova_single_hit * max(self.nova_hit_count - 3, 0),
                ),
            ]

        return nova_state, None

    @view_method
    def validity(self, cooldown_state):
        return Validity(
            name=self.name,
            time_left=max(0, cooldown_state.time_left),
            valid=cooldown_state.available,
            cooldown=self.cooldown,
        )


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

    def get_tick_damage(self, stack_state: StackState):
        return self.tick_damage + self.tick_damage_increment * stack_state.get_stack()

    @reducer_method
    def elapse(
        self,
        time: float,
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        stack_state: StackState,
    ):
        cooldown_state = cooldown_state.copy()
        interval_state = interval_state.copy()
        stack_state = stack_state.copy()

        cooldown_state.elapse(time)

        dealing_events = []

        for _ in interval_state.resolving(time):
            dealing_events.append(
                self.event_provider.dealt(
                    self.get_tick_damage(stack_state), self.tick_hit
                )
            )
            stack_state.increase(1)

        return (cooldown_state, interval_state, stack_state), [
            self.event_provider.elapsed(time)
        ] + dealing_events

    @reducer_method
    def use(
        self,
        payload: None,
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        stack_state: StackState,
        dynamics: Dynamics,
    ):
        stack_state = stack_state.copy()

        (
            cooldown_state,
            interval_state,
            dynamics,
        ), events = self.use_tick_emitting_trait(
            cooldown_state, interval_state, dynamics
        )
        if not is_rejected(events):
            stack_state.reset(1)

        return (cooldown_state, interval_state, stack_state, dynamics), events

    @view_method
    def validity(self, cooldown_state: CooldownState):
        return self.validity_in_cooldown_trait(cooldown_state)

    @view_method
    def running(self, interval_state: IntervalState) -> Running:
        return Running(
            name=self.name,
            time_left=interval_state.interval_time_left,
            duration=self._get_duration(),
        )

    def _get_duration(self) -> float:
        return self.duration

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit

    def _get_tick_damage_hit(self) -> tuple[float, float]:
        return self.tick_damage, self.tick_hit
