from typing import Optional, TypedDict

import simaple.simulate.component.trait.common.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.common.periodic_trait as periodic_trait
from simaple.core.base import Stat
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Periodic
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class MagicCurcuitFullDriveState(TypedDict):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


# TODO: vary damage multiplier from MP rate
# TODO: trigger on attack skills, not tick
class MagicCurcuitFullDriveComponent(
    SkillComponent,
):
    delay: float
    cooldown_duration: float
    lasting_duration: float

    max_damage_multiplier: float

    periodic_initial_delay: Optional[float] = None
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float

    def get_default_state(self) -> MagicCurcuitFullDriveState:
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(
                interval=self.periodic_interval,
                initial_counter=self.periodic_initial_delay,
                time_left=0,
            ),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    @reducer_method
    def use(self, _: None, state: MagicCurcuitFullDriveState):
        return periodic_trait.start_periodic_with_cooldown(
            state,
            damage=0,
            hit=0,
            delay=self.delay,
            cooldown_duration=self.cooldown_duration,
            lasting_duration=self.lasting_duration,
        )

    @reducer_method
    def elapse(self, time: float, state: MagicCurcuitFullDriveState):
        return periodic_trait.elapse_periodic_with_cooldown(
            state, time, self.periodic_damage, self.periodic_hit
        )

    @view_method
    def validity(self, state: MagicCurcuitFullDriveState):
        return cooldown_trait.validity_view(
            state,
            self.id,
            self.name,
            self.cooldown_duration,
        )

    @view_method
    def buff(self, state: MagicCurcuitFullDriveState) -> Optional[Stat]:
        if state["periodic"].enabled():
            return Stat(damage_multiplier=self.max_damage_multiplier)

        return None

    @view_method
    def running(self, state: MagicCurcuitFullDriveState) -> Running:
        return periodic_trait.running_view(
            state, self.id, self.name, self.lasting_duration
        )
