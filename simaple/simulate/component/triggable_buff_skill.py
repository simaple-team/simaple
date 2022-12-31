from typing import Optional

from pydantic import Field

from simaple.core.base import Stat
from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Lasting
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import BuffTrait, InvalidatableCooldownTrait
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class TriggableBuffState(ReducerState):
    cooldown: Cooldown
    lasting: Lasting
    trigger_cooldown: Cooldown
    dynamics: Dynamics


class TriggableBuffSkillComponent(
    SkillComponent, BuffTrait, InvalidatableCooldownTrait
):
    trigger_cooldown_duration: float
    trigger_damage: float
    trigger_hit: float

    cooldown_duration: float
    delay: float
    lasting_duration: float

    stat: Stat = Field(default_factory=Stat)

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
            "trigger_cooldown": Cooldown(time_left=0),
        }

    @reducer_method
    def use(self, _: None, state: TriggableBuffState):
        return self.use_buff_trait(state)

    @reducer_method
    def elapse(
        self,
        time: float,
        state: TriggableBuffState,
    ):
        state = state.deepcopy()

        state.cooldown.elapse(time)
        state.lasting.elapse(time)
        state.trigger_cooldown.elapse(time)

        return state, [
            self.event_provider.elapsed(time),
        ]

    @reducer_method
    def trigger(
        self,
        _: None,
        state: TriggableBuffState,
    ):
        if not (state.lasting.enabled() and state.trigger_cooldown.available):
            return state, []

        state = state.deepcopy()
        state.trigger_cooldown.set_time_left(self.trigger_cooldown_duration)

        return (
            state,
            [self.event_provider.dealt(self.trigger_damage, self.trigger_hit)],
        )

    @view_method
    def validity(self, state: TriggableBuffState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    @view_method
    def running(self, state: TriggableBuffState) -> Running:
        return self.running_in_buff_trait(state)

    @view_method
    def buff(self, state: TriggableBuffState) -> Optional[Stat]:
        if state.lasting.enabled():
            return self.stat
        return None

    def _get_lasting_duration(self, state: TriggableBuffState) -> float:
        return self.lasting_duration
