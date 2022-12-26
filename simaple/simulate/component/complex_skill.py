from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Duration
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import (
    DurableTrait,
    InvalidatableCooldownTrait,
)
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class SynergyState(ReducerState):
    cooldown: Cooldown
    duration: Duration
    dynamics: Dynamics


class SynergySkillComponent(SkillComponent, DurableTrait, InvalidatableCooldownTrait):
    name: str
    damage: float
    hit: float
    cooldown: float
    delay: float

    synergy: Stat
    duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "duration": Duration(time_left=0),
        }

    @reducer_method
    def use(self, _: None, state: SynergyState):
        state = state.copy()
        if not state.cooldown.available:
            return state, self.event_provider.rejected()

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self.cooldown)
        )
        state.duration.set_time_left(
            self.duration
        )  # note that synergy do not works with dynamic duration.

        return state, [
            self.event_provider.dealt(self.damage, self.hit),
            self.event_provider.delayed(self.delay),
        ]

    @reducer_method
    def elapse(self, time: float, state: SynergyState):
        return self.elapse_durable_trait(time, state)

    @view_method
    def validity(self, state: SynergyState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    @view_method
    def buff(self, state: SynergyState) -> Optional[Stat]:
        if state.duration.enabled():
            return self.synergy

        return Stat()

    @view_method
    def running(self, state: SynergyState) -> Running:
        return self.running_in_durable_trait(state)

    def _get_duration(self, state: SynergyState) -> float:
        return self.duration
