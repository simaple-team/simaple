from typing import TypedDict

import simaple.simulate.component.trait.common.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.common.simple_attack as simple_attack
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.entity import Cooldown
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.global_property import Dynamics


class DOTEmittingState(TypedDict):
    cooldown: Cooldown
    dynamics: Dynamics


class DOTEmittingAttackSkillComponent(
    SkillComponent,
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
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    @reducer_method
    def elapse(self, time: float, state: DOTEmittingState):
        return simple_attack.elapse(state, time)

    @reducer_method
    def use(self, _: None, state: DOTEmittingState):
        state, event = simple_attack.use_cooldown_attack(
            state, self.cooldown_duration, self.damage, self.hit, self.delay
        )
        event += [
            simple_attack.get_dot_event(
                self.name, self.dot_damage, self.dot_lasting_duration
            )
        ]
        return state, event

    @reducer_method
    def reset_cooldown(self, _: None, state: DOTEmittingState):
        cooldown = state["cooldown"].model_copy()
        cooldown.set_time_left(0)
        state["cooldown"] = cooldown

        return state, []

    @view_method
    def validity(self, state: DOTEmittingState):
        return cooldown_trait.validity_view(
            state, self.id, self.name, self.cooldown_duration
        )
