from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.base import Event, State
from simaple.simulate.component.base import Component, reducer_method, view_method
from simaple.simulate.component.skill import (
    AttackSkillComponent,
    CooldownState,
    IntervalState,
    StackState,
    TickDamageConfiguratedAttackSkillComponent,
)
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


class DivineAttackSkillComponent(AttackSkillComponent):
    binds: dict[str, str] = {
        "divine_mark": ".바하뮤트.divine_mark",
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


class DivineMinion(TickDamageConfiguratedAttackSkillComponent):
    mark_advantage: Stat

    def get_default_state(self):
        return {
            "divine_mark": DivineMarkState(),
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
