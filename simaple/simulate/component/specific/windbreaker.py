from typing import Optional, TypedDict

import simaple.simulate.component.trait.consumable_trait as consumable_trait
import simaple.simulate.component.trait.periodic_trait as periodic_trait
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.entity import Consumable, Integer, Periodic
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class HowlingGaleState(TypedDict):
    consumable: Consumable
    consumed: Integer
    periodic: Periodic
    dynamics: Dynamics


class HowlingGaleComponentProps(TypedDict):
    id: str
    name: str
    delay: float
    maximum_stack: int
    cooldown_duration: float
    periodic_initial_delay: Optional[float]
    periodic_interval: float
    periodic_damage: list[list[float]]
    periodic_hit: list[list[float]]
    lasting_duration: float


class HowlingGaleComponent(
    SkillComponent,
):
    name: str
    delay: float
    maximum_stack: int

    cooldown_duration: float

    periodic_initial_delay: Optional[float] = None
    periodic_interval: float
    periodic_damage: list[list[float]]
    periodic_hit: list[list[float]]

    lasting_duration: float

    def get_default_state(self) -> HowlingGaleState:
        return {
            "consumable": Consumable(
                maximum_stack=self.maximum_stack,
                stack=self.maximum_stack,
                cooldown_duration=self.cooldown_duration,
                time_left=self.cooldown_duration,
            ),
            "consumed": Integer(value=0),
            "periodic": Periodic(
                interval=self.periodic_interval,
                initial_counter=self.periodic_initial_delay,
                time_left=0,
            ),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> HowlingGaleComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "delay": self.delay,
            "maximum_stack": self.maximum_stack,
            "cooldown_duration": self.cooldown_duration,
            "periodic_initial_delay": self.periodic_initial_delay,
            "periodic_interval": self.periodic_interval,
            "periodic_damage": self.periodic_damage,
            "periodic_hit": self.periodic_hit,
            "lasting_duration": self.lasting_duration,
        }

    @reducer_method
    def elapse(self, time: float, state: HowlingGaleState):
        consumable, periodic = (
            state["consumable"].model_copy(),
            state["periodic"].model_copy(),
        )

        consumable.elapse(time)

        dealing_events = []
        consumed = state["consumed"].get_value()
        for _ in range(periodic.elapse(time)):
            for periodic_damage, periodic_hit in zip(
                self.periodic_damage[consumed - 1], self.periodic_hit[consumed - 1]
            ):
                dealing_events.append(
                    self.event_provider.dealt(periodic_damage, periodic_hit)
                )

        state["consumable"] = consumable
        state["periodic"] = periodic

        return state, [self.event_provider.elapsed(time)] + dealing_events

    @reducer_method
    def use(self, _: None, state: HowlingGaleState):
        if not state["consumable"].available:
            return state, [self.event_provider.rejected()]

        consumable, consumed, periodic = (
            state["consumable"].model_copy(),
            state["consumed"].model_copy(),
            state["periodic"].model_copy(),
        )

        consumed_count = min(consumable.get_stack(), len(self.periodic_damage))
        consumed.set_value(consumed_count)
        consumable.stack -= consumed_count

        periodic.set_time_left(self._get_lasting_duration())

        state["consumable"] = consumable
        state["consumed"] = consumed
        state["periodic"] = periodic

        return state, [
            self.event_provider.delayed(self.delay),
        ]

    @view_method
    def validity(self, state: HowlingGaleState):
        return consumable_trait.consumable_validity(
            state, self.id, self.name, self.cooldown_duration
        )

    @view_method
    def running(self, state: HowlingGaleState) -> Running:
        props = self.get_props()
        return periodic_trait.running_view(
            state,
            id=props["id"],
            name=props["name"],
            lasting_duration=self._get_lasting_duration(),
        )

    def _get_lasting_duration(self) -> float:
        return self.lasting_duration + self.delay
