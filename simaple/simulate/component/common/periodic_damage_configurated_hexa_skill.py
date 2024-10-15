from typing import Optional, TypedDict

import simaple.simulate.component.trait.common.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.common.periodic_trait as periodic_trait
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Periodic
from simaple.simulate.component.feature import DamageAndHit
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.util import is_rejected
from simaple.simulate.component.view import Running
from simaple.simulate.event import EmptyEvent
from simaple.simulate.global_property import Dynamics


class PeriodicDamageHexaState(TypedDict):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class PeriodicDamageConfiguratedHexaSkillComponent(
    SkillComponent,
):
    """
    PeriodicDamageConfiguratedHexaSkillComponent
    This describes skill that act like:
    - various Initial damage x hit
      + periodic damage x hit
    """

    name: str
    damage_and_hits: list[DamageAndHit]
    delay: float

    cooldown_duration: float

    periodic_initial_delay: Optional[float] = None
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float

    lasting_duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(
                interval=self.periodic_interval,
                initial_counter=self.delay,
                time_left=0,
            ),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    @reducer_method
    def elapse(self, time: float, state: PeriodicDamageHexaState):
        return periodic_trait.elapse_periodic_with_cooldown(
            state, time, self.periodic_damage, self.periodic_hit
        )

    @reducer_method
    def use(self, _: None, state: PeriodicDamageHexaState):
        state, events = periodic_trait.start_periodic_with_cooldown(
            state,
            0,
            0,
            self.delay,
            self.cooldown_duration,
            self.lasting_duration,
        )

        if is_rejected(events):
            return state, events

        return (
            state,
            [
                EmptyEvent.dealt(entry.damage, entry.hit)
                for entry in self.damage_and_hits
            ]
            + events,
        )

    @view_method
    def validity(self, state: PeriodicDamageHexaState):
        return cooldown_trait.validity_view(
            state,
            self.id,
            self.name,
            self.cooldown_duration,
        )

    @view_method
    def running(self, state: PeriodicDamageHexaState) -> Running:
        return periodic_trait.running_view(
            state, self.id, self.name, self.lasting_duration
        )
