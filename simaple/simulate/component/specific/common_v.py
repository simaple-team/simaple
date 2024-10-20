from typing import TypedDict

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.entity import Cooldown
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.view import Running
from simaple.simulate.core.base import Entity
from simaple.simulate.event import EmptyEvent
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


class ProgrammedPeriodicState(TypedDict):
    cooldown: Cooldown
    programmed_periodic: ProgrammedPeriodic
    dynamics: Dynamics


class ProgrammedPeriodicComponentProps(TypedDict):
    id: str
    name: str
    damage: float
    hit: float
    delay: float
    cooldown_duration: float
    periodic_intervals: list[float]
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float


class ProgrammedPeriodicComponent(SkillComponent):
    name: str
    damage: float
    hit: float
    delay: float

    cooldown_duration: float

    periodic_intervals: list[float]
    periodic_damage: float
    periodic_hit: float

    lasting_duration: float

    def get_default_state(self) -> ProgrammedPeriodicState:
        return {
            "cooldown": Cooldown(time_left=0),
            "programmed_periodic": ProgrammedPeriodic(
                intervals=self.periodic_intervals, time_left=0
            ),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> ProgrammedPeriodicComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "damage": self.damage,
            "hit": self.hit,
            "delay": self.delay,
            "cooldown_duration": self.cooldown_duration,
            "periodic_intervals": self.periodic_intervals,
            "periodic_damage": self.periodic_damage,
            "periodic_hit": self.periodic_hit,
            "lasting_duration": self.lasting_duration,
        }

    @reducer_method
    def elapse(self, time: float, state: ProgrammedPeriodicState):
        cooldown, programmed_periodic = (
            state["cooldown"].model_copy(),
            state["programmed_periodic"].model_copy(),
        )

        cooldown.elapse(time)

        lapse_count = 0
        for _ in programmed_periodic.resolving(time):
            lapse_count += 1

        state["programmed_periodic"] = programmed_periodic
        state["cooldown"] = cooldown

        return state, [EmptyEvent.elapsed(time)] + [
            EmptyEvent.dealt(self.periodic_damage, self.periodic_hit)
            for _ in range(lapse_count)
        ]

    @reducer_method
    def use(self, _: None, state: ProgrammedPeriodicState):
        if not state["cooldown"].available:
            return state, [self.event_provider.rejected()]

        cooldown, programmed_periodic = (
            state["cooldown"].model_copy(),
            state["programmed_periodic"].model_copy(),
        )

        cooldown.set_time_left(
            state["dynamics"].stat.calculate_cooldown(self.cooldown_duration)
        )
        programmed_periodic.set_time_left(self.lasting_duration)

        state["cooldown"] = cooldown
        state["programmed_periodic"] = programmed_periodic

        return state, [
            EmptyEvent.dealt(self.damage, self.hit),
            EmptyEvent.delayed(self._get_delay()),
        ]

    @view_method
    def validity(self, state: ProgrammedPeriodicState):
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def running(self, state: ProgrammedPeriodicState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state["programmed_periodic"].time_left,
            lasting_duration=self.lasting_duration,
        )
