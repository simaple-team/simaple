from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Keydown
from simaple.simulate.component.skill import Cooldown, SkillComponent
from simaple.simulate.component.trait.impl import (
    CooldownValidityTrait,
    KeydownSkillTrait,
    UseSimpleAttackTrait,
)
from simaple.simulate.component.util import is_rejected
from simaple.simulate.global_property import Dynamics


class FinalCutState(ReducerState):
    cooldown: Cooldown
    dynamics: Dynamics


class FinalCutComponent(SkillComponent, UseSimpleAttackTrait, CooldownValidityTrait):
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    sudden_raid_cooltime_reduce: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, state: FinalCutState):
        return self.elapse_simple_attack(time, state)

    @reducer_method
    def use(self, _: None, state: FinalCutState):
        return self.use_simple_attack(state)

    @reducer_method
    def sudden_raid(self, _: None, state: FinalCutState):
        state = state.deepcopy()
        state.cooldown.set_time_left(
            state.cooldown.time_left * (100 - self.sudden_raid_cooltime_reduce) / 100
        )
        return state, []

    @view_method
    def validity(self, state: FinalCutState):
        return self.validity_in_cooldown_trait(state)

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit


class BladeStormState(ReducerState):
    cooldown: Cooldown
    keydown: Keydown
    dynamics: Dynamics


class BladeStormComponent(SkillComponent, KeydownSkillTrait, CooldownValidityTrait):
    maximum_keydown_time: float

    damage: float
    hit: float
    delay: float
    cooldown_duration: float

    keydown_prepare_delay: float
    keydown_end_delay: float

    prepare_damage: float
    prepare_hit: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "keydown": Keydown(interval=self.delay, running=False),
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: BladeStormState,
    ):
        state, events = self.use_keydown_trait(state)

        if not is_rejected(events):
            events.append(
                self.event_provider.dealt(self.prepare_damage, self.prepare_hit)
            )

        return state, events

    @reducer_method
    def elapse(self, time: float, state: BladeStormState):
        state, events = self.elapse_keydown_trait(time, state)
        return state, events

    @reducer_method
    def stop(self, _, state: BladeStormState):
        state, events = self.stop_keydown_trait(state)
        return state, events

    @view_method
    def validity(self, state: BladeStormState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def keydown(self, state: BladeStormState):
        return self.keydown_view_in_keydown_trait(state)

    def _get_maximum_keydown_time_prepare_delay(self) -> tuple[float, float]:
        return self.maximum_keydown_time, self.keydown_prepare_delay

    def _get_keydown_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit

    def _get_keydown_end_damage_hit_delay(self) -> tuple[float, float, float]:
        return 0, 0, self.keydown_end_delay
