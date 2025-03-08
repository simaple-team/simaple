from typing import Optional, TypedDict

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.periodic_trait as periodic_trait
from simaple.simulate.component.base import Component, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Periodic
from simaple.simulate.component.view import Running
from simaple.simulate.event import EmptyEvent
from simaple.simulate.global_property import Dynamics


class PeriodicDamageSkillState(TypedDict):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class PeriodicDamageSkillComponentProps(TypedDict):
    id: str
    name: str
    delay: float
    cooldown_duration: float
    periodic_initial_delay: Optional[float]
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float

    finish_damage: Optional[float]
    finish_hit: Optional[float]

class PeriodicDamageSkillComponent(
    Component,
):
    name: str
    delay: float

    cooldown_duration: float

    periodic_initial_delay: Optional[float] = None
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float

    lasting_duration: float

    finish_damage: Optional[float] = None
    finish_hit: Optional[float] = None

    def get_default_state(self) -> PeriodicDamageSkillState:
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(
                interval=self.periodic_interval,
                initial_counter=self.periodic_initial_delay,
                time_left=0,
            ),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> PeriodicDamageSkillComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "delay": self.delay,
            "cooldown_duration": self.cooldown_duration,
            "periodic_initial_delay": self.periodic_initial_delay,
            "periodic_interval": self.periodic_interval,
            "periodic_damage": self.periodic_damage,
            "periodic_hit": self.periodic_hit,
            "lasting_duration": self.lasting_duration,
            "finish_damage": self.finish_damage,
            "finish_hit": self.finish_hit,
        }

    @reducer_method
    def elapse(self, time: float, state: PeriodicDamageSkillState):
        was_running = state["periodic"].enabled()
        state, events = periodic_trait.elapse_periodic_with_cooldown(
            state,
            {"time": time},
            **self.get_props(),
        )
        is_running = state["periodic"].enabled()

        # 종료 시점에 데미지 추가
        if (
            self.finish_hit is not None
            and self.finish_damage is not None
            and was_running
            and not is_running
        ):  
            events.append(
                self.event_provider.dealt(self.finish_damage, self.finish_hit)
            )

        return state, events

    @reducer_method
    def use(self, _: None, state: PeriodicDamageSkillState):
        return periodic_trait.start_periodic_with_cooldown(
            state,
            {},
            **self.get_props(),
            damage=0,
            hit=0,
        )

    @view_method
    def validity(self, state: PeriodicDamageSkillState):
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def running(self, state: PeriodicDamageSkillState) -> Running:
        return periodic_trait.running_view(
            state,
            **self.get_props(),
        )
