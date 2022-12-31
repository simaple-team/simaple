from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Lasting
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import BuffTrait, CooldownValidityTrait
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class UltimateDarkSightState(ReducerState):
    cooldown: Cooldown
    lasting: Lasting
    dynamics: Dynamics


class UltimateDarkSightComponent(SkillComponent, BuffTrait, CooldownValidityTrait):
    cooldown_duration: float
    delay: float
    lasting_duration: float

    final_damage_multiplier: float
    advanced_dark_sight_final_damage_multiplier: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
        }

    @reducer_method
    def use(self, _: None, state: UltimateDarkSightState):
        return self.use_buff_trait(state)

    @reducer_method
    def elapse(self, time: float, state: UltimateDarkSightState):
        return self.elapse_buff_trait(time, state)

    @view_method
    def validity(self, state: UltimateDarkSightState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def buff(self, state: UltimateDarkSightState) -> Optional[Stat]:
        if state.lasting.enabled():
            return Stat(
                final_damage_multiplier=self.final_damage_multiplier
                + self.advanced_dark_sight_final_damage_multiplier
            )

        return None

    @view_method
    def running(self, state: UltimateDarkSightState) -> Running:
        return Running(
            name=self.name,
            time_left=state.lasting.time_left,
            lasting_duration=self._get_lasting_duration(state),
        )

    def _get_lasting_duration(self, state) -> float:
        return self.lasting_duration
