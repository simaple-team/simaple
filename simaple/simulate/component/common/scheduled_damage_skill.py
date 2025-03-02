from typing import Optional, TypedDict
from itertools import accumulate

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.periodic_trait as periodic_trait
from simaple.simulate.component.base import Component, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Periodic, Schedule
from simaple.simulate.component.view import Running
from simaple.simulate.event import EmptyEvent
from simaple.simulate.global_property import Dynamics
from simaple.simulate.component.feature import DamageSchedule


class ScheduledDamageSkillState(TypedDict):
    cooldown: Cooldown
    schedule: Schedule
    dynamics: Dynamics


class ScheduledDamageSkillComponentProps(TypedDict):
    id: str
    name: str
    delay: float
    cooldown_duration: float
    damage_schedule: list[DamageSchedule]


class ScheduledDamageSkillComponent(
    Component,
):
    """
    MultipleAttackSkillComponent
    This describes skill that act like:
    - various Initial damage x hit
    """

    name: str
    delay: float
    cooldown_duration: float
    damage_schedule: list[DamageSchedule]  # relative times

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "schedule": Schedule(
                scheduled_times=list(
                    accumulate([entry.time for entry in self.damage_schedule])
                )
            ),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> ScheduledDamageSkillComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "delay": self.delay,
            "cooldown_duration": self.cooldown_duration,
            "damage_schedule": self.damage_schedule,
        }

    @reducer_method
    def elapse(self, time: float, state: ScheduledDamageSkillState):
        cooldown, schedule = state["cooldown"].model_copy(), state["schedule"].model_copy()
        cooldown.elapse(time)

        index_start, index_end = schedule.elapse(time)

        state["cooldown"] = cooldown
        state["schedule"] = schedule

        return state, [
            self.event_provider.dealt(entry.damage, entry.hit)
            for entry in self.damage_schedule[index_start:index_end]
        ] + [self.event_provider.elapsed(time)]

    @reducer_method
    def use(self, _: None, state: ScheduledDamageSkillState):
        if not state["cooldown"].available:
            return state, [self.event_provider.rejected()]

        cooldown, schedule = state["cooldown"].model_copy(), state["schedule"].model_copy()

        cooldown.set_time_left(
            state["dynamics"].stat.calculate_cooldown(self.cooldown_duration)
        )
        index_start, index_end = schedule.start()

        state["cooldown"] = cooldown    
        state["schedule"] = schedule

        return state, [
            self.event_provider.dealt(entry.damage, entry.hit)
            for entry in self.damage_schedule[index_start:index_end]
        ] + [
            self.event_provider.delayed(self.delay),
        ]

    @view_method
    def validity(self, state: ScheduledDamageSkillState):
        return cooldown_trait.validity_view(state, **self.get_props())
