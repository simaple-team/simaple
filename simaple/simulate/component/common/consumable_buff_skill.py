from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Consumable, Lasting
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import (
    ConsumableBuffTrait,
    ConsumableValidityTrait,
)
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class ConsumableBuffSkillState(ReducerState):
    consumable: Consumable
    lasting: Lasting
    dynamics: Dynamics


class ConsumableBuffSkillComponent(
    SkillComponent, ConsumableBuffTrait, ConsumableValidityTrait
):
    stat: Stat
    cooldown_duration: float
    delay: float
    lasting_duration: float
    maximum_stack: int
    apply_buff_duration: bool = True

    def get_default_state(self):
        return {
            "consumable": Consumable(
                time_left=self.cooldown_duration,
                cooldown_duration=self.cooldown_duration,
                maximum_stack=self.maximum_stack,
                stack=self.maximum_stack,
            ),
            "lasting": Lasting(time_left=0),
        }

    @reducer_method
    def use(self, _: None, state: ConsumableBuffSkillState):
        return self.use_consumable_buff_trait(
            state, apply_buff_duration=self.apply_buff_duration
        )

    @reducer_method
    def elapse(self, time: float, state: ConsumableBuffSkillState):
        return self.elapse_consumable_buff_trait(time, state)

    @view_method
    def validity(self, state: ConsumableBuffSkillState):
        return self.validity_in_consumable_trait(state)

    @view_method
    def buff(self, state: ConsumableBuffSkillState) -> Optional[Stat]:
        if state.lasting.enabled():
            return self.stat

        return None

    @view_method
    def running(self, state: ConsumableBuffSkillState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state.lasting.time_left,
            lasting_duration=self._get_lasting_duration(state),
        )

    def _get_lasting_duration(self, state) -> float:
        return self.lasting_duration
