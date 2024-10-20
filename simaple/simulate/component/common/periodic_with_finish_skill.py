from typing import Optional, TypedDict

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.periodic_trait as periodic_trait
from simaple.simulate.component.base import Component, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Periodic
from simaple.simulate.component.view import Running
from simaple.simulate.event import EmptyEvent
from simaple.simulate.global_property import Dynamics


class PeriodicWithFinishState(TypedDict):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class PeriodicWithFinishSkillComponentProps(TypedDict):
    id: str
    name: str
    delay: float
    cooldown_duration: float
    periodic_initial_delay: Optional[float]
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    finish_damage: float
    finish_hit: float
    lasting_duration: float


class PeriodicWithFinishSkillComponent(
    Component,
):
    name: str
    delay: float

    cooldown_duration: float

    periodic_initial_delay: Optional[float] = None
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float

    finish_damage: float
    finish_hit: float

    lasting_duration: float

    def get_default_state(self) -> PeriodicWithFinishState:
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(
                interval=self.periodic_interval,
                initial_counter=self.periodic_initial_delay,
                time_left=0,
            ),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> PeriodicWithFinishSkillComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "delay": self.delay,
            "cooldown_duration": self.cooldown_duration,
            "periodic_initial_delay": self.periodic_initial_delay,
            "periodic_interval": self.periodic_interval,
            "periodic_damage": self.periodic_damage,
            "periodic_hit": self.periodic_hit,
            "finish_damage": self.finish_damage,
            "finish_hit": self.finish_hit,
            "lasting_duration": self.lasting_duration,
        }

    @reducer_method
    def elapse(self, time: float, state: PeriodicWithFinishState):
        was_running = state["periodic"].enabled()
        state, events = periodic_trait.elapse_periodic_with_cooldown(
            state,
            {"time": time},
            **self.get_props(),
        )

        if not state["periodic"].enabled() and was_running:
            events.append(EmptyEvent.dealt(self.finish_damage, self.finish_hit))

        return state, events

    @reducer_method
    def use(self, _: None, state: PeriodicWithFinishState):
        return periodic_trait.start_periodic_with_cooldown(
            state,
            {},
            **self.get_props(),
            damage=0,
            hit=0,
        )

    @view_method
    def validity(self, state: PeriodicWithFinishState):
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def running(self, state: PeriodicWithFinishState) -> Running:
        return periodic_trait.running_view(
            state,
            **self.get_props(),
        )
