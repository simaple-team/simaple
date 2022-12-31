from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.skill import Cooldown, SkillComponent
from simaple.simulate.component.trait.impl import (
    CooldownValidityTrait,
    UseSimpleAttackTrait,
)
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

    listening_actions: dict[str, str] = {
        "써든레이드.use.emitted.global.delay": "sudden_raid"
    }

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
