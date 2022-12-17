from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.state import CooldownState, DurationState
from simaple.simulate.component.view import Running, Validity
from simaple.simulate.global_property import Dynamics


class SynergySkillComponent(SkillComponent):
    name: str
    damage: float
    hit: float
    cooldown: float = 0.0
    delay: float

    synergy: Stat
    duration: float

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
            "duration_state": DurationState(time_left=0),
        }

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        duration_state: DurationState,
        dynamics: Dynamics,
    ):
        cooldown_state = cooldown_state.copy()
        duration_state = duration_state.copy()

        if not cooldown_state.available:
            return (
                cooldown_state,
                duration_state,
                dynamics,
            ), self.event_provider.rejected()

        cooldown_state.set_time_left(dynamics.stat.calculate_cooldown(self.cooldown))
        duration_state.set_time_left(
            self.duration
        )  # synerge do not works with dynamic duration.

        return (cooldown_state, duration_state, dynamics), [
            self.event_provider.dealt(self.damage, self.hit),
            self.event_provider.delayed(self.delay),
        ]

    @reducer_method
    def elapse(
        self, time: float, cooldown_state: CooldownState, duration_state: DurationState
    ):
        cooldown_state = cooldown_state.copy()
        duration_state = duration_state.copy()

        cooldown_state.elapse(time)
        duration_state.elapse(time)

        return (cooldown_state, duration_state), [
            self.event_provider.elapsed(time),
        ]

    @view_method
    def validity(self, cooldown_state: CooldownState):
        return self.invalidate_if_disabled(
            Validity(
                name=self.name,
                time_left=max(0, cooldown_state.time_left),
                valid=cooldown_state.available,
                cooldown=self.cooldown,
            )
        )

    @view_method
    def buff(self, duration_state: DurationState) -> Optional[Stat]:
        if duration_state.enabled():
            return self.synergy

        return Stat()

    @view_method
    def running(self, duration_state: DurationState) -> Running:
        return Running(name=self.name, time_left=duration_state.time_left)
