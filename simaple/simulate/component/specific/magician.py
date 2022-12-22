from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.state import CooldownState, DurationState
from simaple.simulate.component.trait.impl import CooldownValidityTrait, DurableTrait
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class Infinity(SkillComponent, DurableTrait, CooldownValidityTrait):
    cooldown: float
    delay: float
    duration: float

    final_damage_increment: float
    increase_interval: float
    default_final_damage: float
    maximum_final_damage: float

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
            "duration_state": DurationState(time_left=0),
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
        self, time: float, cooldown_state: CooldownState, duration_state: DurationState
    ):
        return self.elapse_durable_trait(time, cooldown_state, duration_state)

    @view_method
    def validity(self, cooldown_state: CooldownState):
        return self.validity_in_cooldown_trait(cooldown_state)

    @view_method
    def buff(self, duration_state: DurationState) -> Optional[Stat]:
        if duration_state.enabled():
            return self.get_infinity_effect(duration_state)

        return None

    @view_method
    def running(self, duration_state: DurationState) -> Running:
        return Running(
            name=self.name,
            time_left=duration_state.time_left,
            duration=self._get_duration(),
        )

    def get_infinity_effect(self, duration_state) -> Stat:
        elapsed = duration_state.get_elapsed_time()
        tick_count = elapsed // self.increase_interval
        final_damage_multiplier = min(
            self.default_final_damage + self.final_damage_increment * tick_count,
            self.maximum_final_damage,
        )
        return Stat(final_damage_multiplier=final_damage_multiplier)

    def _get_duration(self) -> float:
        return self.duration
