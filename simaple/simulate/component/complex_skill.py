from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.state_fragment import CooldownState, DurationState
from simaple.simulate.component.trait.impl import (
    DurableTrait,
    InvalidatableCooldownTrait,
)
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class SynergeState(ReducerState):
    cooldown_state: CooldownState
    duration_state: DurationState
    dynamics: Dynamics


class SynergySkillComponent(SkillComponent, DurableTrait, InvalidatableCooldownTrait):
    name: str
    damage: float
    hit: float
    cooldown: float = 0.0
    delay: float

    synergy: Stat
    duration: float

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
            "duration_state": DurationState(time_left=0),
        }

    @reducer_method
    def use(self, _: None, state: SynergeState):
        state = state.copy()
        if not state.cooldown_state.available:
            return state, self.event_provider.rejected()

        state.cooldown_state.set_time_left(
            state.dynamics.stat.calculate_cooldown(self.cooldown)
        )
        state.duration_state.set_time_left(
            self.duration
        )  # note that synergy do not works with dynamic duration.

        return state, [
            self.event_provider.dealt(self.damage, self.hit),
            self.event_provider.delayed(self.delay),
        ]

    @reducer_method
    def elapse(self, time: float, state: SynergeState):
        return self.elapse_durable_trait(time, state)

    @view_method
    def validity(self, state: SynergeState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    @view_method
    def buff(self, state: SynergeState) -> Optional[Stat]:
        if state.duration_state.enabled():
            return self.synergy

        return Stat()

    @view_method
    def running(self, state: SynergeState) -> Running:
        return Running(
            name=self.name,
            time_left=state.duration_state.time_left,
            duration=self._get_duration(),
        )

    def _get_duration(self) -> float:
        return self.duration
