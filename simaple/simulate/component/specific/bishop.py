from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.base import State
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.state import CooldownState, IntervalState
from simaple.simulate.component.trait.impl import (
    CooldownValidityTrait,
    InvalidatableCooldownTrait,
    TickEmittingTrait,
    UseSimpleAttackTrait,
)
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class DivineMarkState(State):
    advantage: Optional[Stat]

    def mark(self, advantage: Stat):
        self.advantage = advantage

    def consume_mark(self) -> Stat:
        self.advantage, advantage = None, self.advantage
        if advantage is None:
            advantage = Stat()

        return advantage


class DivineAttackSkillComponent(
    SkillComponent, CooldownValidityTrait, UseSimpleAttackTrait
):
    binds: dict[str, str] = {
        "divine_mark": ".바하뮤트.divine_mark",
    }
    name: str
    damage: float
    hit: float
    cooldown: float
    delay: float
    synergy: Optional[Stat]

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
        }

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        divine_mark: DivineMarkState,
        dynamics: Dynamics,
    ):
        cooldown_state = cooldown_state.copy()
        divine_mark = divine_mark.copy()

        if not cooldown_state.available:
            return (
                cooldown_state,
                divine_mark,
                dynamics,
            ), self.event_provider.rejected()

        cooldown_state.set_time_left(dynamics.stat.calculate_cooldown(self.cooldown))

        modifier = divine_mark.consume_mark()

        return (cooldown_state, divine_mark, dynamics), [
            self.event_provider.dealt(self.damage, self.hit, modifier=modifier),
            self.event_provider.delayed(self.delay),
        ]

    @reducer_method
    def elapse(self, time: float, cooldown_state: CooldownState):
        return self.elapse_simple_attack(time, cooldown_state)

    @view_method
    def validity(self, cooldown_state):
        return self.validity_in_cooldown_trait(cooldown_state)

    @view_method
    def buff(self):
        return self.synergy

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit


class DivineMinion(SkillComponent, TickEmittingTrait, InvalidatableCooldownTrait):
    name: str
    damage: float
    hit: float
    cooldown: float
    delay: float

    tick_interval: float
    tick_damage: float
    tick_hit: float
    duration: float

    mark_advantage: Stat
    stat: Optional[Stat]

    def get_default_state(self):
        if self.name == "바하뮤트":
            return {
                "divine_mark": DivineMarkState(),
                "cooldown_state": CooldownState(time_left=0),
                "interval_state": IntervalState(
                    interval=self.tick_interval, time_left=0
                ),
            }

        return {
            "cooldown_state": CooldownState(time_left=0),
            "interval_state": IntervalState(interval=self.tick_interval, time_left=0),
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        divine_mark: DivineMarkState,
    ):
        cooldown_state = cooldown_state.copy()
        interval_state = interval_state.copy()

        cooldown_state.elapse(time)
        dealing_events = []

        for _ in interval_state.resolving(time):
            divine_mark.mark(self.mark_advantage)
            dealing_events.append(
                self.event_provider.dealt(
                    self.tick_damage,
                    self.tick_hit,
                )
            )

        return (cooldown_state, interval_state, divine_mark), [
            self.event_provider.elapsed(time)
        ] + dealing_events

    @view_method
    def buff(self, interval_state: IntervalState):
        if interval_state.enabled():
            return self.stat

        return None

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        dynamics: Dynamics,
    ):
        return self.use_tick_emitting_trait(cooldown_state, interval_state, dynamics)

    @view_method
    def validity(self, cooldown_state: CooldownState):
        return self.validity_in_invalidatable_cooldown_trait(cooldown_state)

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
