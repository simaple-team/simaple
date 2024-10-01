from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Lasting
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import BuffTrait, InvalidatableCooldownTrait
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class BuffSkillState(ReducerState):
    cooldown: Cooldown
    lasting: Lasting
    dynamics: Dynamics


class BuffSkillComponent(SkillComponent, BuffTrait, InvalidatableCooldownTrait):
    stat: Stat
    cooldown_duration: float
    delay: float
    lasting_duration: float
    apply_buff_duration: bool = True
    # TODO: use apply_cooldown_reduction argument to apply cooltime reduction

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
        }

    @reducer_method
    def use(self, _: None, state: BuffSkillState):
        return self.use_buff_trait(state, apply_buff_duration=self.apply_buff_duration)

    @reducer_method
    def elapse(self, time: float, state: BuffSkillState):
        return self.elapse_buff_trait(time, state)

    @view_method
    def validity(self, state: BuffSkillState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    @view_method
    def buff(self, state: BuffSkillState) -> Optional[Stat]:
        if state.lasting.enabled():
            return self.stat

        return None

    @view_method
    def running(self, state: BuffSkillState) -> Running:
        return self.running_in_buff_trait(state)

    def _get_lasting_duration(self, state: BuffSkillState) -> float:
        return self.lasting_duration
