from typing import Optional, TypedDict

import simaple.simulate.component.trait.consumable_trait as consumable_trait
import simaple.simulate.component.trait.lasting_trait as lasting_trait
from simaple.core.base import Stat
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.entity import Consumable, Lasting
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class ConsumableBuffSkillState(TypedDict):
    consumable: Consumable
    lasting: Lasting
    dynamics: Dynamics


class ConsumableBuffSkillComponentProps(TypedDict):
    id: str
    name: str
    stat: Stat
    cooldown_duration: float
    delay: float
    lasting_duration: float
    maximum_stack: int
    apply_buff_duration: bool


class ConsumableBuffSkillComponent(
    SkillComponent,
):
    stat: Stat
    cooldown_duration: float
    delay: float
    lasting_duration: float
    maximum_stack: int
    apply_buff_duration: bool = True

    def get_default_state(self) -> ConsumableBuffSkillState:
        return {
            "consumable": Consumable(
                time_left=self.cooldown_duration,
                cooldown_duration=self.cooldown_duration,
                maximum_stack=self.maximum_stack,
                stack=self.maximum_stack,
            ),
            "lasting": Lasting(time_left=0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> ConsumableBuffSkillComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "stat": self.stat,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
            "lasting_duration": self.lasting_duration,
            "maximum_stack": self.maximum_stack,
            "apply_buff_duration": self.apply_buff_duration,
        }

    @reducer_method
    def use(self, _: None, state: ConsumableBuffSkillState):
        return consumable_trait.start_consumable_buff(
            state,
            lasting_duration=self.lasting_duration,
            delay=self.delay,
            apply_buff_duration=self.apply_buff_duration,
        )

    @reducer_method
    def elapse(self, time: float, state: ConsumableBuffSkillState):
        return consumable_trait.elapse_consumable_buff(state, time)

    @view_method
    def validity(self, state: ConsumableBuffSkillState):
        return consumable_trait.consumable_validity(
            state, self.id, self.name, self.cooldown_duration
        )

    @view_method
    def buff(self, state: ConsumableBuffSkillState) -> Optional[Stat]:
        if state["lasting"].enabled():
            return self.stat

        return None

    @view_method
    def running(self, state: ConsumableBuffSkillState) -> Running:
        return lasting_trait.running_view(state, **self.get_props())
