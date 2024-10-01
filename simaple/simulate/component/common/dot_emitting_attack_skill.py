from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import (
    AddDOTDamageTrait,
    InvalidatableCooldownTrait,
    UseSimpleAttackTrait,
)
from simaple.simulate.global_property import Dynamics


class DOTEmittingState(ReducerState):
    cooldown: Cooldown
    dynamics: Dynamics


class DOTEmittingAttackSkillComponent(
    SkillComponent, InvalidatableCooldownTrait, UseSimpleAttackTrait, AddDOTDamageTrait
):
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    dot_damage: float
    dot_lasting_duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, state: DOTEmittingState):
        return self.elapse_simple_attack(time, state)

    @reducer_method
    def use(self, _: None, state: DOTEmittingState):
        state, event = self.use_simple_attack(state)
        event += [self.get_dot_add_event()]
        return state, event

    @reducer_method
    def reset_cooldown(self, _: None, state: DOTEmittingState):
        state = state.deepcopy()
        state.cooldown.set_time_left(0)
        return state, None

    @view_method
    def validity(self, state: DOTEmittingState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit

    def _get_dot_damage_and_lasting(self) -> tuple[float, float]:
        return self.dot_damage, self.dot_lasting_duration
