from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.skill import (
    CooldownState,
    DurationState,
    SkillComponent,
)
from simaple.simulate.component.trait.impl import CooldownValidityTrait, DurableTrait
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class PenalizedBuffSkillState(ReducerState):
    cooldown_state: CooldownState
    duration_state: DurationState
    dynamics: Dynamics


class PenalizedBuffSkill(SkillComponent, CooldownValidityTrait, DurableTrait):
    advantage: Stat
    disadvantage: Stat
    cooldown: float
    delay: float
    duration: float

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
            "duration_state": DurationState(time_left=0),
        }

    @reducer_method
    def use(self, _: None, state: PenalizedBuffSkillState):
        return self.use_durable_trait(state)

    @reducer_method
    def elapse(self, time: float, state: PenalizedBuffSkillState):
        return self.elapse_durable_trait(time, state)

    @view_method
    def validity(self, state: PenalizedBuffSkillState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def buff(self, state: PenalizedBuffSkillState) -> Optional[Stat]:
        if state.duration_state.enabled():
            return self.advantage

        if not (state.duration_state.enabled() or state.cooldown_state.available):
            return self.disadvantage

        return None

    @view_method
    def running(self, state: PenalizedBuffSkillState) -> Running:
        return Running(
            name=self.name,
            time_left=state.duration_state.time_left,
            duration=self._get_duration(),
        )

    def _get_duration(self) -> float:
        return self.duration
