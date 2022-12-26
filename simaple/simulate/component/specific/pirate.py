from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.skill import Cooldown, Lasting, SkillComponent
from simaple.simulate.component.trait.impl import BuffTrait, CooldownValidityTrait
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class PenalizedBuffSkillState(ReducerState):
    cooldown: Cooldown
    lasting: Lasting
    dynamics: Dynamics


class PenalizedBuffSkill(SkillComponent, CooldownValidityTrait, BuffTrait):
    advantage: Stat
    disadvantage: Stat
    cooldown_duration: float
    delay: float
    lasting_duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
        }

    @reducer_method
    def use(self, _: None, state: PenalizedBuffSkillState):
        return self.use_buff_trait(state)

    @reducer_method
    def elapse(self, time: float, state: PenalizedBuffSkillState):
        return self.elapse_buff_trait(time, state)

    @view_method
    def validity(self, state: PenalizedBuffSkillState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def buff(self, state: PenalizedBuffSkillState) -> Optional[Stat]:
        if state.lasting.enabled():
            return self.advantage

        if not (state.lasting.enabled() or state.cooldown.available):
            return self.disadvantage

        return None

    @view_method
    def running(self, state: PenalizedBuffSkillState) -> Running:
        return Running(
            name=self.name,
            time_left=state.lasting.time_left,
            lasting_duration=self._get_lasting_duration(state),
        )

    def _get_lasting_duration(self, state: PenalizedBuffSkillState) -> float:
        return self.lasting_duration
