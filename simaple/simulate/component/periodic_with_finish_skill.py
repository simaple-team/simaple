from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Periodic
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import (
    CooldownValidityTrait,
    PeriodicElapseTrait,
    UsePeriodicDamageTrait,
)
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class PeriodicWithFinishState(ReducerState):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class PeriodicWithFinishSkillComponent(
    SkillComponent, UsePeriodicDamageTrait, PeriodicElapseTrait, CooldownValidityTrait
):
    name: str
    delay: float

    cooldown_duration: float

    periodic_interval: float
    periodic_damage: float
    periodic_hit: float

    finish_damage: float
    finish_hit: float

    lasting_duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(interval=self.periodic_interval, time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, state: PeriodicWithFinishState):
        was_running = state.periodic.enabled()
        state, events = self.elapse_periodic_damage_trait(time, state)
        if not state.periodic.enabled() and was_running:
            events.append(
                self.event_provider.dealt(self.finish_damage, self.finish_hit)
            )

        return state, events

    @reducer_method
    def use(self, _: None, state: PeriodicWithFinishState):
        return self.use_periodic_damage_trait(state)

    @view_method
    def validity(self, state: PeriodicWithFinishState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def running(self, state: PeriodicWithFinishState) -> Running:
        return Running(
            name=self.name,
            time_left=state.periodic.time_left,
            lasting_duration=self._get_lasting_duration(state),
        )

    def _get_lasting_duration(self, state: PeriodicWithFinishState) -> float:
        return self.lasting_duration

    def _get_periodic_damage_hit(
        self, state: PeriodicWithFinishState
    ) -> tuple[float, float]:
        return self.periodic_damage, self.periodic_hit
