from typing import Optional, TypedDict

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.lasting_trait as lasting_trait
from simaple.core.base import Stat
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Lasting
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.util import is_rejected
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class SynergyState(TypedDict):
    cooldown: Cooldown
    lasting: Lasting
    dynamics: Dynamics


class SynergySkillComponentProps(TypedDict):
    id: str
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float
    synergy: Stat
    lasting_duration: float


class SynergySkillComponent(SkillComponent):
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    synergy: Stat
    lasting_duration: float

    def get_default_state(self) -> SynergyState:
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> SynergySkillComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "damage": self.damage,
            "hit": self.hit,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
            "synergy": self.synergy,
            "lasting_duration": self.lasting_duration,
        }

    @reducer_method
    def use(self, _: None, state: SynergyState):
        state, events = lasting_trait.start_lasting_with_cooldown(
            state, {}, **self.get_props(), apply_buff_duration=False
        )

        if is_rejected(events):
            return state, events

        return (
            state,
            [
                self.event_provider.dealt(self.damage, self.hit),
            ]
            + events,
        )

    @reducer_method
    def elapse(self, time: float, state: SynergyState):
        return lasting_trait.elapse_lasting_with_cooldown(
            state, {"time": time}, **self.get_props()
        )

    @view_method
    def validity(self, state: SynergyState):
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def buff(self, state: SynergyState) -> Optional[Stat]:
        if state["lasting"].enabled():
            return self.synergy

        return Stat()

    @view_method
    def running(self, state: SynergyState) -> Running:
        return lasting_trait.running_view(state, **self.get_props())
