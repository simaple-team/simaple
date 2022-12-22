from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.skill import (
    CooldownState,
    DurationState,
    SkillComponent,
)
from simaple.simulate.component.trait.impl import CooldownValidityTrait, DurableTrait
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


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
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        duration_state: DurationState,
        dynamics: Dynamics,
    ):
        return self.use_durable_trait(cooldown_state, duration_state, dynamics)

    @reducer_method
    def elapse(
        self, time: float, cooldown_state: CooldownState, duration_state: DurationState
    ):
        return self.elapse_durable_trait(time, cooldown_state, duration_state)

    @view_method
    def validity(self, cooldown_state: CooldownState):
        return self.validity_in_cooldown_trait(cooldown_state)

    @view_method
    def buff(
        self, cooldown_state: CooldownState, duration_state: DurationState
    ) -> Optional[Stat]:
        if duration_state.enabled():
            return self.advantage

        if not (duration_state.enabled() or cooldown_state.available):
            return self.disadvantage

        return None

    @view_method
    def running(self, duration_state: DurationState) -> Running:
        return Running(
            name=self.name,
            time_left=duration_state.time_left,
            duration=self._get_duration(),
        )

    def _get_duration(self) -> float:
        return self.duration
