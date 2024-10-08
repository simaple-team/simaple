from typing import Optional

from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Periodic
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import (
    InvalidatableCooldownTrait,
    PeriodicWithSimpleDamageTrait,
)
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class PeriodicDamageState(ReducerState):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class PeriodicDamageConfiguratedAttackSkillComponent(
    SkillComponent, PeriodicWithSimpleDamageTrait, InvalidatableCooldownTrait
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

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(
                interval=self.periodic_interval,
                initial_counter=self.periodic_initial_delay,
                time_left=0,
            ),
        }

    @reducer_method
    def elapse(self, time: float, state: PeriodicDamageState):
        return self.elapse_periodic_damage_trait(time, state)

    @reducer_method
    def use(self, _: None, state: PeriodicDamageState):
        return self.use_periodic_damage_trait(state)

    @view_method
    def validity(self, state: PeriodicDamageState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    @view_method
    def running(self, state: PeriodicDamageState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state.periodic.time_left,
            lasting_duration=self._get_lasting_duration(state),
        )

    def _get_lasting_duration(self, state: PeriodicDamageState) -> float:
        return self.lasting_duration

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit

    def _get_periodic_damage_hit(
        self, state: PeriodicDamageState
    ) -> tuple[float, float]:
        return self.periodic_damage, self.periodic_hit
