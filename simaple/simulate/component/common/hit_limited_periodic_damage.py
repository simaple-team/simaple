from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Periodic
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import (
    CooldownValidityTrait,
    UsePeriodicDamageTrait,
)
from simaple.simulate.global_property import Dynamics


class HitLimitedPeriodicDamageState(ReducerState):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class HitLimitedPeriodicDamageComponent(
    SkillComponent, UsePeriodicDamageTrait, CooldownValidityTrait
):
    name: str
    cooldown_duration: float
    delay: float

    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float

    max_count: int

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(interval=self.periodic_interval, time_left=0),
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        state: HitLimitedPeriodicDamageState,
    ):
        state = state.deepcopy()

        state.cooldown.elapse(time)
        dealing_events = []

        for _ in state.periodic._resolving(time):
            if state.periodic.count >= self.max_count:
                break

            dealing_events.append(
                self.event_provider.dealt(
                    self.periodic_damage,
                    self.periodic_hit,
                )
            )

        if state.periodic.count >= self.max_count:
            state.periodic.disable()

        return state, [self.event_provider.elapsed(time)] + dealing_events

    @reducer_method
    def use(self, _: None, state: HitLimitedPeriodicDamageState):
        return self.use_periodic_damage_trait(state)

    @view_method
    def validity(self, state: HitLimitedPeriodicDamageState):
        return self.validity_in_cooldown_trait(state)

    def _get_lasting_duration(self, state: HitLimitedPeriodicDamageState) -> float:
        return self.lasting_duration
