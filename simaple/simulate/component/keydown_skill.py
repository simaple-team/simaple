from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Keydown
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import (
    CooldownValidityTrait,
    KeydownSkillTrait,
)
from simaple.simulate.global_property import Dynamics


class KeydownSkillState(ReducerState):
    cooldown: Cooldown
    keydown: Keydown
    dynamics: Dynamics


class KeydownSkillComponent(SkillComponent, KeydownSkillTrait, CooldownValidityTrait):
    maximum_keydown_time: float

    damage: float
    hit: float
    delay: float
    cooldown_duration: float

    keydown_prepare_delay: float
    keydown_end_delay: float

    finish_damage: float
    finish_hit: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "keydown": Keydown(interval=self.delay, running=False),
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: KeydownSkillState,
    ):
        return self.use_keydown_trait(state)

    @reducer_method
    def elapse(self, time: float, state: KeydownSkillState):
        state, events = self.elapse_keydown_trait(time, state)
        return state, events

    @reducer_method
    def stop(self, _, state: KeydownSkillState):
        state, events = self.stop_keydown_trait(state)
        return state, events

    @view_method
    def validity(self, state: KeydownSkillState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def keydown(self, state: KeydownSkillState):
        return self.keydown_view_in_keydown_trait(state)

    def _get_maximum_keydown_time_prepare_delay(self) -> tuple[float, float]:
        return self.maximum_keydown_time, self.keydown_prepare_delay

    def _get_keydown_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit

    def _get_keydown_end_damage_hit_delay(self) -> tuple[float, float, float]:
        return self.finish_damage, self.finish_hit, self.keydown_end_delay
