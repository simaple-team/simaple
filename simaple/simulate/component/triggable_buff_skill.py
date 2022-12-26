from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.state_fragment import CooldownState, DurationState
from simaple.simulate.component.trait.impl import (
    DurableTrait,
    InvalidatableCooldownTrait,
)
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class TriggableBuffState(ReducerState):
    cooldown_state: CooldownState
    duration_state: DurationState
    trigger_cooldown_state: CooldownState
    dynamics: Dynamics


class TriggableBuffSkill(SkillComponent, DurableTrait, InvalidatableCooldownTrait):
    trigger_cooldown: float
    trigger_damage: float
    trigger_hit: float

    cooldown: float = 0.0
    delay: float
    duration: float

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
            "duration_state": DurationState(time_left=0),
            "trigger_cooldown_state": CooldownState(time_left=0),
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

        state.cooldown_state.elapse(time)
        state.duration_state.elapse(time)
        state.trigger_cooldown_state.elapse(time)

        return state, [
            self.event_provider.elapsed(time),
        ]

    @reducer_method
    def trigger(
        self,
        _: None,
        state: TriggableBuffState,
    ):
        if not (
            state.duration_state.enabled() and state.trigger_cooldown_state.available
        ):
            return state, []

        state = state.copy()
        state.trigger_cooldown_state.set_time_left(self.trigger_cooldown)

        return (
            state,
            self.event_provider.dealt(self.trigger_damage, self.trigger_hit),
        )

    @view_method
    def validity(self, state: TriggableBuffState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    @view_method
    def running(self, state: TriggableBuffState) -> Running:
        return Running(
            name=self.name,
            time_left=state.duration_state.time_left,
            duration=self._get_duration(),
        )

    def _get_duration(self) -> float:
        return self.duration
