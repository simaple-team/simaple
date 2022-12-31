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

    def set_time_left(self, time: float):
        self.time_left = time
        self.count = 0

    def enabled(self):
        return self.time_left > 0

    def resolving(self, time: float):
        self.interval_counter -= time

        # pylint:disable=chained-comparison
        while self.interval_counter <= 0 and self.time_left > 0:
            interval = self.intervals[self.count % len(self.intervals)]
            self.interval_counter += interval
            self.time_left -= interval
            yield 1
            self.count += 1

    def disable(self):
        self.time_left = 0


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
        state = state.deepcopy()
        state.cooldown.elapse(time)

        lapse_count = 0
        for _ in state.programmed_periodic.resolving(time):
            lapse_count += 1

        return state, [self.event_provider.elapsed(time)] + [
            self.event_provider.dealt(self.periodic_damage, self.periodic_hit)
            for _ in range(lapse_count)
        ]

    @reducer_method
    def use(self, _: None, state: ProgrammedPeriodicState):
        state = state.deepcopy()

        if not state.cooldown.available:
            return state, [self.event_provider.rejected()]

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown_duration())
        )
        state.programmed_periodic.set_time_left(self.lasting_duration)

        return state, [
            self.event_provider.dealt(self.damage, self.hit),
            self.event_provider.delayed(self._get_delay()),
        ]

    @view_method
    def validity(self, state: ProgrammedPeriodicState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    @view_method
    def running(self, state: ProgrammedPeriodicState) -> Running:
        return Running(
            name=self.name,
            time_left=state.programmed_periodic.time_left,
            lasting_duration=self.lasting_duration,
        )
