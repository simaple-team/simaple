from simaple.simulate.base import Entity
from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import InvalidatableCooldownTrait
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class ProgrammedPeriodic(Entity):
    interval_counter: float = 0.0
    intervals: list[float]
    time_left: float = 0.0
    count: int = 0

    def enabled(self):
        return self.time_left > 0

    def set_time_left(self, time: float):
        return self.model_copy(
            update={
                "time_left": time,
                "count": 0,
            }
        )

    def elapse(self, time: float):
        if self.time_left <= 0:
            return self, 0

        interval_counter = self.interval_counter - time
        time_left_counter = self.time_left
        lapse_count = 0

        while interval_counter <= 0 and time_left_counter > 0:
            interval = self.intervals[(self.count + lapse_count) % len(self.intervals)]
            interval_counter += interval
            time_left_counter -= interval
            lapse_count += 1

        return self.model_copy(
            update={
                "interval_counter": interval_counter,
                "time_left": self.time_left - time,
                "count": self.count + lapse_count,
            }
        ), lapse_count

    def disable(self):
        return self.model_copy(
            update={
                "time_left": 0,
            }
        )


class ProgrammedPeriodicState(ReducerState):
    cooldown: Cooldown
    programmed_periodic: ProgrammedPeriodic
    dynamics: Dynamics


class ProgrammedPeriodicComponent(SkillComponent, InvalidatableCooldownTrait):
    name: str
    damage: float
    hit: float
    delay: float

    cooldown_duration: float

    periodic_intervals: list[float]
    periodic_damage: float
    periodic_hit: float

    lasting_duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "programmed_periodic": ProgrammedPeriodic(
                intervals=self.periodic_intervals, time_left=0
            ),
        }

    @reducer_method
    def elapse(self, time: float, state: ProgrammedPeriodicState):
        cooldown = state.cooldown.elapse(time)

        programmed_periodic, lapse_count = state.programmed_periodic.elapse(time)

        return state.copy(
            {
                "cooldown": cooldown,
                "programmed_periodic": programmed_periodic,
            }
        ), [self.event_provider.elapsed(time)] + [
            self.event_provider.dealt(self.periodic_damage, self.periodic_hit)
            for _ in range(lapse_count)
        ]

    @reducer_method
    def use(self, _: None, state: ProgrammedPeriodicState):
        if not state.cooldown.available:
            return state, [self.event_provider.rejected()]

        cooldown = state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown_duration())
        )
        programmed_periodic = state.programmed_periodic.set_time_left(
            self.lasting_duration
        )

        return state.copy(
            {"cooldown": cooldown, "programmed_periodic": programmed_periodic}
        ), [
            self.event_provider.dealt(self.damage, self.hit),
            self.event_provider.delayed(self._get_delay()),
        ]

    @view_method
    def validity(self, state: ProgrammedPeriodicState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    @view_method
    def running(self, state: ProgrammedPeriodicState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state.programmed_periodic.time_left,
            lasting_duration=self.lasting_duration,
        )
