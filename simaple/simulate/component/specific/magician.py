from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Lasting
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import BuffTrait, CooldownValidityTrait
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class InfinityState(ReducerState):
    cooldown: Cooldown
    lasting: Lasting
    dynamics: Dynamics


class Infinity(SkillComponent, BuffTrait, CooldownValidityTrait):
    cooldown_duration: float
    delay: float
    lasting_duration: float

    final_damage_increment: float
    increase_interval: float
    default_final_damage: float
    maximum_final_damage: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
        }

    @reducer_method
    def use(self, _: None, state: InfinityState):
        return self.use_buff_trait(state)

    @reducer_method
    def elapse(self, time: float, state: InfinityState):
        return self.elapse_buff_trait(time, state)

    @view_method
    def validity(self, state: InfinityState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def buff(self, state: InfinityState) -> Optional[Stat]:
        if state.lasting.enabled():
            return self.get_infinity_effect(state)

        return None

    @view_method
    def running(self, state: InfinityState) -> Running:
        return Running(
            name=self.name,
            time_left=state.lasting.time_left,
            lasting_duration=self._get_lasting_duration(state),
        )

    def get_infinity_effect(self, state: InfinityState) -> Stat:
        elapsed = state.lasting.get_elapsed_time()
        tick_count = elapsed // self.increase_interval
        final_damage_multiplier = min(
            self.default_final_damage + self.final_damage_increment * tick_count,
            self.maximum_final_damage,
        )
        return Stat(final_damage_multiplier=final_damage_multiplier)

    def _get_lasting_duration(self, state) -> float:
        return self.lasting_duration
