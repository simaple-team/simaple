from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Consumable, Lasting
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import (
    ConsumableBuffTrait,
    ConsumableValidityTrait,
)
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class TranscendentCygnusBlessingState(ReducerState):
    lasting: Lasting
    dynamics: Dynamics
    consumable: Consumable


class TranscendentCygnusBlessing(
    SkillComponent, ConsumableBuffTrait, ConsumableValidityTrait
):
    cooldown_duration: float
    delay: float
    lasting_duration: float

    damage_increment: float
    increase_interval: float
    default_damage: float
    maximum_damage: float
    maximum_stack: int

    def get_default_state(self):
        return {
            "consumable": Consumable(
                time_left=self.cooldown_duration,
                cooldown_duration=self.cooldown_duration,
                maximum_stack=self.maximum_stack,
                stack=self.maximum_stack,
            ),
            "lasting": Lasting(time_left=0),
        }

    @reducer_method
    def use(self, _: None, state: TranscendentCygnusBlessingState):
        return self.use_consumable_buff_trait(state)

    @reducer_method
    def elapse(self, time: float, state: TranscendentCygnusBlessingState):
        return self.elapse_consumable_buff_trait(time, state)

    @view_method
    def validity(self, state: TranscendentCygnusBlessingState):
        return self.validity_in_consumable_trait(state)

    @view_method
    def buff(self, state: TranscendentCygnusBlessingState) -> Optional[Stat]:
        if state.lasting.enabled():
            return self.get_infinity_effect(state)

        return None

    @view_method
    def running(self, state: TranscendentCygnusBlessingState) -> Running:
        return Running(
            name=self.name,
            time_left=state.lasting.time_left,
            lasting_duration=self._get_lasting_duration(state),
        )

    def get_infinity_effect(self, state: TranscendentCygnusBlessingState) -> Stat:
        elapsed = state.lasting.get_elapsed_time()
        tick_count = elapsed // self.increase_interval
        damage_multiplier = min(
            self.default_damage + self.damage_increment * tick_count,
            self.maximum_damage,
        )
        return Stat(damage_multiplier=damage_multiplier)

    def _get_lasting_duration(self, state) -> float:
        return self.lasting_duration
