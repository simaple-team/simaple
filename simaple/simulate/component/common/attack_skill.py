from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import (
    InvalidatableCooldownTrait,
    UseSimpleAttackTrait,
)
from simaple.simulate.component.util import ignore_rejected
from simaple.simulate.global_property import Dynamics


class AttackSkillState(ReducerState):
    cooldown: Cooldown
    dynamics: Dynamics


class AttackSkillComponent(
    SkillComponent, InvalidatableCooldownTrait, UseSimpleAttackTrait
):
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, state: AttackSkillState):
        return self.elapse_simple_attack(time, state)

    @reducer_method
    def use(self, _: None, state: AttackSkillState):
        return self.use_simple_attack(state)

    @reducer_method
    @ignore_rejected
    def use_with_ignore_reject(self, _: None, state: AttackSkillState):
        """
        This method is used to ignore the rejected event.
        Useful when automatic triggering is needed.
        """
        return self.use_simple_attack(state)

    @reducer_method
    def reset_cooldown(self, _: None, state: AttackSkillState):
        state = state.deepcopy()
        state.cooldown.set_time_left(0)
        return state, None

    @view_method
    def validity(self, state: AttackSkillState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit
