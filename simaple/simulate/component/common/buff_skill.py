from typing import Optional, TypedDict

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.lasting_trait as lasting_trait
from simaple.core.base import Stat
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Lasting
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class BuffSkillState(TypedDict):
    cooldown: Cooldown
    lasting: Lasting
    dynamics: Dynamics


class BuffSkillComponent(SkillComponent):
    stat: Stat
    cooldown_duration: float
    delay: float
    lasting_duration: float
    apply_buff_duration: bool = True
    # TODO: use apply_cooldown_reduction argument to apply cooltime reduction

    def get_default_state(self) -> BuffSkillState:
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    @reducer_method
    def use(self, _: None, state: BuffSkillState):
        return lasting_trait.start_lasting_with_cooldown(
            state,
            self.cooldown_duration,
            self.lasting_duration,
            self.delay,
            apply_buff_duration=self.apply_buff_duration,
        )

    @reducer_method
    def elapse(self, time: float, state: BuffSkillState):
        return lasting_trait.elapse_lasting_with_cooldown(state, time)

    @view_method
    def validity(self, state: BuffSkillState):
        return cooldown_trait.validity_view(
            state,
            self.id,
            self.name,
            self.cooldown_duration,
        )

    @view_method
    def buff(self, state: BuffSkillState) -> Optional[Stat]:
        if state["lasting"].enabled():
            return self.stat

        return None

    @view_method
    def running(self, state: BuffSkillState) -> Running:
        return lasting_trait.running_view(state, self.id, self.name)
