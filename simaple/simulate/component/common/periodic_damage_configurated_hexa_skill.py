from typing import Optional

from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Periodic
from simaple.simulate.component.feature import DamageAndHit
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import (
    InvalidatableCooldownTrait,
    PeriodicElapseTrait,
)
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class PeriodicDamageHexaState(ReducerState):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class PeriodicDamageConfiguratedHexaSkillComponent(
    SkillComponent, PeriodicElapseTrait, InvalidatableCooldownTrait
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
        }

    @reducer_method
    def elapse(self, time: float, state: PeriodicDamageHexaState):
        return self.elapse_periodic_damage_trait(time, state)

    @reducer_method
    def use(self, _: None, state: PeriodicDamageHexaState):
        if not state.cooldown.available:
            return state, [self.event_provider.rejected()]

        state = state.deepcopy()

        delay = self._get_delay()

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown_duration())
        )
        state.periodic.set_time_left(self._get_lasting_duration(state))

        return state, [
            self.event_provider.dealt(entry.damage, entry.hit)
            for entry in self.damage_and_hits
        ] + [
            self.event_provider.delayed(delay),
        ]

    @view_method
    def validity(self, state: PeriodicDamageHexaState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    @view_method
    def running(self, state: PeriodicDamageHexaState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state.periodic.time_left,
            lasting_duration=self._get_lasting_duration(state),
        )

    def _get_lasting_duration(self, state: PeriodicDamageHexaState) -> float:
        return self.lasting_duration

    def _get_periodic_damage_hit(
        self, state: PeriodicDamageHexaState
    ) -> tuple[float, float]:
        return self.periodic_damage, self.periodic_hit
