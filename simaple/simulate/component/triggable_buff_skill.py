from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Duration
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import (
    DurableTrait,
    InvalidatableCooldownTrait,
)
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class TriggableBuffState(ReducerState):
    cooldown: Cooldown
    duration: Duration
    trigger_cooldown: Cooldown
    dynamics: Dynamics


class TriggableBuffSkill(SkillComponent, DurableTrait, InvalidatableCooldownTrait):
    trigger_cooldown: float
    trigger_damage: float
    trigger_hit: float

    cooldown: float
    delay: float
    duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "duration": Duration(time_left=0),
            "trigger_cooldown": Cooldown(time_left=0),
        }

    @reducer_method
    def use(self, _: None, state: TriggableBuffState):
        return self.use_durable_trait(state)

    @reducer_method
    def elapse(
        self,
        time: float,
        state: TriggableBuffState,
    ):
        state = state.copy()

        state.cooldown.elapse(time)
        state.duration.elapse(time)
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
        if not (state.duration.enabled() and state.trigger_cooldown.available):
            return state, []

        state = state.copy()
        state.trigger_cooldown.set_time_left(self.trigger_cooldown)

        return (
            state,
            self.event_provider.dealt(self.trigger_damage, self.trigger_hit),
        )

    @view_method
    def validity(self, state: TriggableBuffState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    @view_method
    def running(self, state: TriggableBuffState) -> Running:
        return self.running_in_durable_trait(state)

    def _get_duration(self, state: TriggableBuffState) -> float:
        return self.duration
