from typing import Optional, TypedDict

import simaple.simulate.component.trait.common.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.common.periodic_trait as periodic_trait
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Periodic
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.global_property import Dynamics


class HitLimitedPeriodicDamageState(TypedDict):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class HitLimitedPeriodicDamageComponent(
    SkillComponent,
):
    name: str
    cooldown_duration: float
    delay: float

    periodic_initial_delay: Optional[float] = None
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float

    max_count: int

    def get_default_state(self) -> HitLimitedPeriodicDamageState:
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
    def elapse(
        self,
        time: float,
        state: HitLimitedPeriodicDamageState,
    ):
        periodic, cooldown = (
            state["periodic"].model_copy(),
            state["cooldown"].model_copy(),
        )

        cooldown.elapse(time)
        dealing_events = []

        time_to_resolve = time
        periodic_state = periodic
        previous_count = periodic_state.count

        while time_to_resolve > 0:
            periodic_state, time_to_resolve = periodic_state.resolve_step(
                periodic_state, time_to_resolve
            )

            if periodic_state.count >= self.max_count:
                break

            if previous_count < periodic_state.count:
                dealing_events.append(
                    self.event_provider.dealt(
                        self.periodic_damage,
                        self.periodic_hit,
                    )
                )

                previous_count = periodic_state.count

        if periodic_state.count >= self.max_count:
            periodic_state.disable()

        state["periodic"] = periodic_state
        state["cooldown"] = cooldown

        return state, [self.event_provider.elapsed(time)] + dealing_events

    @reducer_method
    def use(self, _: None, state: HitLimitedPeriodicDamageState):
        return periodic_trait.start_periodic_with_cooldown(
            state,
            damage=0,
            hit=0,
            delay=self.delay,
            cooldown_duration=self.cooldown_duration,
            lasting_duration=self.lasting_duration,
        )

    @view_method
    def validity(self, state: HitLimitedPeriodicDamageState):
        return cooldown_trait.validity_view(
            state,
            self.id,
            self.name,
            self.cooldown_duration,
        )
