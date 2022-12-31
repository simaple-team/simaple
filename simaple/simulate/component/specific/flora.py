from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Periodic
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import (
    CooldownValidityTrait,
    PeriodicWithSimpleDamageTrait,
)
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class MagicCurcuitFullDriveState(ReducerState):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


# TODO: vary damage multiplier from MP rate
# TODO: trigger on attack skills, not tick
class MagicCurcuitFullDriveComponent(
    SkillComponent, CooldownValidityTrait, PeriodicWithSimpleDamageTrait
):
    delay: float
    cooldown_duration: float
    lasting_duration: float

    max_damage_multiplier: float

    periodic_interval: float
    periodic_damage: float
    periodic_hit: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(interval=self.periodic_interval),
        }

    @reducer_method
    def use(self, _: None, state: MagicCurcuitFullDriveState):
        return self.use_periodic_damage_trait(state)

    @reducer_method
    def elapse(self, time: float, state: MagicCurcuitFullDriveState):
        return self.elapse_periodic_damage_trait(time, state)

    @view_method
    def validity(self, state: MagicCurcuitFullDriveState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def buff(self, state: MagicCurcuitFullDriveState) -> Optional[Stat]:
        if state.periodic.enabled():
            return Stat(damage_multiplier=self.max_damage_multiplier)

        return None

    @view_method
    def running(self, state: MagicCurcuitFullDriveState) -> Running:
        return Running(
            name=self.name,
            time_left=state.periodic.time_left,
            lasting_duration=self.lasting_duration,
        )

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        # TODO: TickEmittingTrait should not extend SimpleDamageTrait. Remove this method
        return 0, 0

    def _get_periodic_damage_hit(self, state) -> tuple[float, float]:
        return self.periodic_damage, self.periodic_hit

    def _get_lasting_duration(self, state) -> float:
        return self.lasting_duration
