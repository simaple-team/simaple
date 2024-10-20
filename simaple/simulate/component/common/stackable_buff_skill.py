from typing import Optional, TypedDict

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.lasting_trait as lasting_trait
from simaple.core.base import Stat
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Lasting, Stack
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class StackableBuffSkillState(TypedDict):
    cooldown: Cooldown
    lasting: Lasting
    stack: Stack
    dynamics: Dynamics


class StackableBuffSkillComponentProps(TypedDict):
    id: str
    name: str
    stat: Stat
    cooldown_duration: float
    delay: float
    lasting_duration: float
    maximum_stack: int
    apply_buff_duration: bool


class StackableBuffSkillComponent(
    SkillComponent,
):
    stat: Stat
    cooldown_duration: float
    delay: float
    lasting_duration: float
    maximum_stack: int
    apply_buff_duration: bool = True
    # TODO: use apply_cooldown_reduction argument to apply cooltime reduction

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
            "stack": Stack(maximum_stack=self.maximum_stack),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> StackableBuffSkillComponentProps:
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
    def use(
        self,
        _: None,
        state: StackableBuffSkillState,
    ):
        stack = state["stack"].model_copy()
        if state["lasting"].time_left <= 0:
            stack.reset()
        stack.increase()

        state["stack"] = stack

        return lasting_trait.start_lasting_with_cooldown(
            state,
            self.cooldown_duration,
            self.lasting_duration,
            self.delay,
            apply_buff_duration=self.apply_buff_duration,
        )

    @reducer_method
    def elapse(
        self,
        time: float,
        state: StackableBuffSkillState,
    ):
        return lasting_trait.elapse_lasting_with_cooldown(state, time)

    @view_method
    def validity(self, state: StackableBuffSkillState):
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def buff(self, state: StackableBuffSkillState) -> Optional[Stat]:
        if state["lasting"].enabled():
            return self.stat.stack(state["stack"].stack)

        return None

    @view_method
    def running(self, state: StackableBuffSkillState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state["lasting"].time_left,
            lasting_duration=state["lasting"].assigned_duration,
            stack=state["stack"].stack if state["lasting"].time_left > 0 else 0,
        )
