from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.state import CooldownState, DurationState
from simaple.simulate.component.trait.impl import (
    DurableTrait,
    InvalidatableCooldownTrait,
)
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class TriggableBuffSkill(SkillComponent, DurableTrait, InvalidatableCooldownTrait):
    trigger_cooldown: float
    trigger_damage: float
    trigger_hit: float

    cooldown: float
    delay: float
    duration: float

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
            "duration_state": DurationState(time_left=0),
            "trigger_cooldown_state": CooldownState(time_left=0),
        }

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        duration_state: DurationState,
        dynamics: Dynamics,
    ):
        return self.use_durable_trait(cooldown_state, duration_state, dynamics)

    @reducer_method
    def elapse(
        self,
        time: float,
        cooldown_state: CooldownState,
        duration_state: DurationState,
        trigger_cooldown_state: CooldownState,
    ):
        cooldown_state = cooldown_state.copy()
        duration_state = duration_state.copy()
        trigger_cooldown_state = trigger_cooldown_state.copy()

        cooldown_state.elapse(time)
        duration_state.elapse(time)
        trigger_cooldown_state.elapse(time)

        return (cooldown_state, duration_state, trigger_cooldown_state), [
            self.event_provider.elapsed(time),
        ]

    @reducer_method
    def trigger(
        self,
        _: None,
        trigger_cooldown_state: CooldownState,
        duration_state: DurationState,
    ):
        if not (duration_state.enabled() and trigger_cooldown_state.available):
            return (trigger_cooldown_state, duration_state), []

        trigger_cooldown_state = trigger_cooldown_state.copy()
        trigger_cooldown_state.set_time_left(self.trigger_cooldown)

        return (
            (trigger_cooldown_state, duration_state),
            self.event_provider.dealt(self.trigger_damage, self.trigger_hit),
        )

    @view_method
    def validity(self, cooldown_state: CooldownState):
        return self.validity_in_invalidatable_cooldown_trait(cooldown_state)

    @view_method
    def running(self, duration_state: DurationState) -> Running:
        return Running(
            name=self.name,
            time_left=duration_state.time_left,
            duration=self._get_duration(),
        )

    def _get_duration(self) -> float:
        return self.duration
