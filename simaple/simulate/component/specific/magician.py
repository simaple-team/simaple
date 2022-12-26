from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Duration
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import CooldownValidityTrait, DurableTrait
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class InfinityState(ReducerState):
    cooldown: Cooldown
    duration: Duration
    dynamics: Dynamics


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
            "cooldown": Cooldown(time_left=0),
            "duration": Duration(time_left=0),
        }

    @reducer_method
    def use(self, _: None, state: InfinityState):
        return self.use_durable_trait(state)

    @reducer_method
    def elapse(self, time: float, state: InfinityState):
        return self.elapse_durable_trait(time, state)

    @view_method
    def validity(self, state: InfinityState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def buff(self, state: InfinityState) -> Optional[Stat]:
        if state.duration.enabled():
            return self.get_infinity_effect(state)

        return None

    @view_method
    def running(self, state: InfinityState) -> Running:
        return Running(
            name=self.name,
            time_left=state.duration.time_left,
            duration=self._get_duration(state),
        )

    def get_infinity_effect(self, state: InfinityState) -> Stat:
        elapsed = state.duration.get_elapsed_time()
        tick_count = elapsed // self.increase_interval
        final_damage_multiplier = min(
            self.default_final_damage + self.final_damage_increment * tick_count,
            self.maximum_final_damage,
        )
        return Stat(final_damage_multiplier=final_damage_multiplier)

    def _get_duration(self, state) -> float:
        return self.duration
