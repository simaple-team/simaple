from typing import Optional, TypedDict

import simaple.simulate.component.trait.common.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.common.lasting_trait as lasting_trait
from simaple.core.base import Stat
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Lasting
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class PenalizedBuffSkillState(TypedDict):
    cooldown: Cooldown
    lasting: Lasting
    dynamics: Dynamics


class PenalizedBuffSkill(SkillComponent):
    advantage: Stat
    disadvantage: Stat
    cooldown_duration: float
    delay: float
    lasting_duration: float
    apply_buff_duration: bool = True

    def get_default_state(self) -> PenalizedBuffSkillState:
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    @reducer_method
    def use(self, _: None, state: PenalizedBuffSkillState):
        return lasting_trait.start_lasting_with_cooldown(
            state,
            self.cooldown_duration,
            self.lasting_duration,
            self.delay,
            apply_buff_duration=self.apply_buff_duration,
        )

    @reducer_method
    def elapse(self, time: float, state: PenalizedBuffSkillState):
        return lasting_trait.elapse_lasting_with_cooldown(state, time)

    @view_method
    def validity(self, state: PenalizedBuffSkillState):
        return cooldown_trait.validity_view(
            state,
            self.id,
            self.name,
            self.cooldown_duration,
        )

    @view_method
    def buff(self, state: PenalizedBuffSkillState) -> Optional[Stat]:
        if state["lasting"].enabled():
            return self.advantage

        if not (state["lasting"].enabled() or state["cooldown"].available):
            return self.disadvantage

        return None

    @view_method
    def running(self, state: PenalizedBuffSkillState) -> Running:
        return lasting_trait.running_view(
            state,
            self.id,
            self.name,
        )
