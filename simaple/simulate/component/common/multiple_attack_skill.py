from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import (
    InvalidatableCooldownTrait,
    UseSimpleAttackTrait,
)
from simaple.simulate.global_property import Dynamics


class MultipleAttackSkillState(ReducerState):
    cooldown: Cooldown
    dynamics: Dynamics


class MultipleAttackSkillComponent(
    SkillComponent, InvalidatableCooldownTrait, UseSimpleAttackTrait
):
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    multiple: int

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, state: MultipleAttackSkillState):
        return self.elapse_simple_attack(time, state)

    @reducer_method
    def use(self, _: None, state: MultipleAttackSkillState):
        return self.use_multiple_damage(state, self.multiple)

    @reducer_method
    def reset_cooldown(self, _: None, state: MultipleAttackSkillState):
        state = state.deepcopy()
        state.cooldown.set_time_left(0)
        return state, None

    @view_method
    def validity(self, state: MultipleAttackSkillState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit
