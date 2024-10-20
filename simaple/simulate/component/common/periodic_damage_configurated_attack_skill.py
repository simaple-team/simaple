from typing import Optional, TypedDict

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.periodic_trait as periodic_trait
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Periodic
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class PeriodicDamageState(TypedDict):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class PeriodicDamageConfiguratedAttackSkillComponentProps(TypedDict):
    id: str
    name: str
    damage: float
    hit: float
    delay: float
    cooldown_duration: float
    periodic_initial_delay: Optional[float]
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float


class PeriodicDamageConfiguratedAttackSkillComponent(
    SkillComponent,
):
    name: str
    damage: float
    hit: float
    delay: float

    cooldown_duration: float

    periodic_initial_delay: Optional[float] = None
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float

    lasting_duration: float

    def get_default_state(self) -> PeriodicDamageState:
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(
                interval=self.periodic_interval,
                initial_counter=self.periodic_initial_delay,
                time_left=0,
            ),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> PeriodicDamageConfiguratedAttackSkillComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "damage": self.damage,
            "hit": self.hit,
            "delay": self.delay,
            "cooldown_duration": self.cooldown_duration,
            "periodic_initial_delay": self.periodic_initial_delay,
            "periodic_interval": self.periodic_interval,
            "periodic_damage": self.periodic_damage,
            "periodic_hit": self.periodic_hit,
            "lasting_duration": self.lasting_duration,
        }

    @reducer_method
    def elapse(self, time: float, state: PeriodicDamageState):
        return periodic_trait.elapse_periodic_with_cooldown(
            state, time, self.periodic_damage, self.periodic_hit
        )

    @reducer_method
    def use(self, _: None, state: PeriodicDamageState):
        return periodic_trait.start_periodic_with_cooldown(
            state,
            damage=self.damage,
            hit=self.hit,
            delay=self.delay,
            cooldown_duration=self.cooldown_duration,
            lasting_duration=self.lasting_duration,
        )

    @view_method
    def validity(self, state: PeriodicDamageState):
        return cooldown_trait.validity_view(
            state,
            self.get_props(),
        )

    @view_method
    def running(self, state: PeriodicDamageState) -> Running:
        return periodic_trait.running_view(
            state, self.id, self.name, self.lasting_duration
        )
