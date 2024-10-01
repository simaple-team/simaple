from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Lasting, Stack
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import BuffTrait, InvalidatableCooldownTrait
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class StackableBuffSkillState(ReducerState):
    cooldown: Cooldown
    lasting: Lasting
    stack: Stack
    dynamics: Dynamics


class StackableBuffSkillComponent(
    SkillComponent, BuffTrait, InvalidatableCooldownTrait
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
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: StackableBuffSkillState,
    ):
        state = state.deepcopy()
        if state.lasting.time_left <= 0:
            state.stack.reset()
        state.stack.increase()

        return self.use_buff_trait(state, apply_buff_duration=self.apply_buff_duration)

    @reducer_method
    def elapse(
        self,
        time: float,
        state: StackableBuffSkillState,
    ):
        return self.elapse_buff_trait(time, state)

    @view_method
    def validity(self, state: StackableBuffSkillState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    @view_method
    def buff(self, state: StackableBuffSkillState) -> Optional[Stat]:
        if state.lasting.enabled():
            return self.stat.stack(state.stack.stack)

        return None

    @view_method
    def running(self, state: StackableBuffSkillState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state.lasting.time_left,
            lasting_duration=state.lasting.assigned_duration,
            stack=state.stack.stack if state.lasting.time_left > 0 else 0,
        )

    def _get_lasting_duration(self, state: StackableBuffSkillState) -> float:
        return self.lasting_duration
