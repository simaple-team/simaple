from typing import Optional, TypedDict

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.periodic_trait as periodic_trait
from simaple.core.base import Stat
from simaple.simulate.component.base import Component, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Periodic
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class MagicCurcuitFullDriveState(TypedDict):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class MagicCurcuitFullDriveComponentProps(TypedDict):
    id: str
    name: str
    delay: float
    cooldown_duration: float
    lasting_duration: float
    max_damage_multiplier: float
    periodic_initial_delay: Optional[float]
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float


# TODO: vary damage multiplier from MP rate
# TODO: trigger on attack skills, not tick
class MagicCurcuitFullDriveComponent(
    Component,
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

    def get_props(self) -> MagicCurcuitFullDriveComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "delay": self.delay,
            "cooldown_duration": self.cooldown_duration,
            "lasting_duration": self.lasting_duration,
            "max_damage_multiplier": self.max_damage_multiplier,
            "periodic_initial_delay": self.periodic_initial_delay,
            "periodic_interval": self.periodic_interval,
            "periodic_damage": self.periodic_damage,
            "periodic_hit": self.periodic_hit,
        }

    @reducer_method
    def use(self, _: None, state: MagicCurcuitFullDriveState):
        return periodic_trait.start_periodic_with_cooldown(
            state,
            {},
            **self.get_props(),
            damage=0,
            hit=0,
        )

    @reducer_method
    def elapse(self, time: float, state: MagicCurcuitFullDriveState):
        return periodic_trait.elapse_periodic_with_cooldown(
            state, {"time": time}, **self.get_props()
        )

    @view_method
    def validity(self, state: MagicCurcuitFullDriveState):
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def buff(self, state: MagicCurcuitFullDriveState) -> Optional[Stat]:
        if state["periodic"].enabled():
            return Stat(damage_multiplier=self.max_damage_multiplier)

        return None

    @view_method
    def running(self, state: MagicCurcuitFullDriveState) -> Running:
        return periodic_trait.running_view(
            state,
            **self.get_props(),
        )
