from typing import TypedDict

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.keydown_trait as keydown_trait
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Keydown
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.global_property import Dynamics


class KeydownSkillState(TypedDict):
    cooldown: Cooldown
    keydown: Keydown
    dynamics: Dynamics


class KeydownSkillComponentProps(TypedDict):
    name: str
    id: str

    maximum_keydown_time: float
    damage: float
    hit: float
    delay: float
    cooldown_duration: float
    keydown_prepare_delay: float
    keydown_end_delay: float
    finish_damage: float
    finish_hit: float


class KeydownSkillComponent(SkillComponent):
    maximum_keydown_time: float

    damage: float
    hit: float
    delay: float
    cooldown_duration: float

    keydown_prepare_delay: float
    keydown_end_delay: float

    finish_damage: float
    finish_hit: float

    def get_default_state(self) -> KeydownSkillState:
        return {
            "cooldown": Cooldown(time_left=0),
            "keydown": Keydown(interval=self.delay),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> KeydownSkillComponentProps:
        return {
            "name": self.name,
            "id": self.id,
            "maximum_keydown_time": self.maximum_keydown_time,
            "damage": self.damage,
            "hit": self.hit,
            "delay": self.delay,
            "cooldown_duration": self.cooldown_duration,
            "keydown_prepare_delay": self.keydown_prepare_delay,
            "keydown_end_delay": self.keydown_end_delay,
            "finish_damage": self.finish_damage,
            "finish_hit": self.finish_hit,
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: KeydownSkillState,
    ):
        return keydown_trait.use_keydown(
            state,
            self.maximum_keydown_time,
            self.keydown_prepare_delay,
            self.cooldown_duration,
        )

    @reducer_method
    def elapse(self, time: float, state: KeydownSkillState):
        return keydown_trait.elapse_keydown(
            state,
            time,
            self.damage,
            self.hit,
            self.finish_damage,
            self.finish_hit,
            self.keydown_end_delay,
        )

    @reducer_method
    def stop(self, _: None, state: KeydownSkillState):
        return keydown_trait.stop_keydown(
            state, self.finish_damage, self.finish_hit, self.keydown_end_delay
        )

    @view_method
    def validity(self, state: KeydownSkillState):
        return cooldown_trait.validity_view(state, self.get_props())

    @view_method
    def keydown(self, state: KeydownSkillState):
        return keydown_trait.keydown_view(state, self.name)
