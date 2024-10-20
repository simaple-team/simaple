from typing import Optional, TypedDict

from pydantic import Field

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.lasting_trait as lasting_trait
from simaple.core.base import Stat
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Lasting
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class TriggableBuffState(TypedDict):
    cooldown: Cooldown
    lasting: Lasting
    trigger_cooldown: Cooldown
    dynamics: Dynamics


class TriggableBuffSkillComponentProps(TypedDict):
    id: str
    name: str
    stat: Stat
    trigger_cooldown_duration: float
    trigger_damage: float
    trigger_hit: float
    cooldown_duration: float
    delay: float
    lasting_duration: float
    apply_buff_duration: bool


class TriggableBuffSkillComponent(
    SkillComponent,
):
    trigger_cooldown_duration: float
    trigger_damage: float
    trigger_hit: float

    cooldown_duration: float
    delay: float
    lasting_duration: float

    apply_buff_duration: bool = True

    stat: Stat = Field(default_factory=Stat)

    def get_default_state(self) -> TriggableBuffState:
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
            "trigger_cooldown": Cooldown(time_left=0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> TriggableBuffSkillComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "stat": self.stat,
            "trigger_cooldown_duration": self.trigger_cooldown_duration,
            "trigger_damage": self.trigger_damage,
            "trigger_hit": self.trigger_hit,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
            "lasting_duration": self.lasting_duration,
            "apply_buff_duration": self.apply_buff_duration,
        }

    @reducer_method
    def use(self, _: None, state: TriggableBuffState):
        return lasting_trait.start_lasting_with_cooldown(
            state,
            {},
            **self.get_props(),
        )

    @reducer_method
    def elapse(
        self,
        time: float,
        state: TriggableBuffState,
    ):
        cooldown, lasting, trigger_cooldown = (
            state["cooldown"].model_copy(),
            state["lasting"].model_copy(),
            state["trigger_cooldown"].model_copy(),
        )

        cooldown.elapse(time)
        trigger_cooldown.elapse(time)
        lasting.elapse(time)

        state["cooldown"] = cooldown
        state["lasting"] = lasting
        state["trigger_cooldown"] = trigger_cooldown

        return state, [
            self.event_provider.elapsed(time),
        ]

    @reducer_method
    def trigger(
        self,
        _: None,
        state: TriggableBuffState,
    ):
        if not (state["lasting"].enabled() and state["trigger_cooldown"].available):
            return state, []

        trigger_cooldown = state["trigger_cooldown"].model_copy()
        trigger_cooldown.set_time_left(self.trigger_cooldown_duration)

        state["trigger_cooldown"] = trigger_cooldown

        return (
            state,
            [self.event_provider.dealt(self.trigger_damage, self.trigger_hit)],
        )

    @view_method
    def validity(self, state: TriggableBuffState):
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def running(self, state: TriggableBuffState) -> Running:
        return lasting_trait.running_view(state, **self.get_props())

    @view_method
    def buff(self, state: TriggableBuffState) -> Optional[Stat]:
        if state["lasting"].enabled():
            return self.stat

        return None
