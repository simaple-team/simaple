from typing import TypedDict

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.simple_attack as simple_attack
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.entity import Cooldown
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.util import ignore_rejected
from simaple.simulate.core import Event
from simaple.simulate.global_property import Dynamics


class AttackSkillState(TypedDict):
    cooldown: Cooldown
    dynamics: Dynamics


class AttackSkillComponent(
    SkillComponent,
):
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    def get_default_state(self) -> AttackSkillState:
        return {
            "cooldown": Cooldown(time_left=0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    @reducer_method
    def elapse(self, time: float, state: AttackSkillState):
        return simple_attack.elapse(state, time)

    @reducer_method
    def use(
        self, _: None, state: AttackSkillState
    ) -> tuple[AttackSkillState, list[Event]]:
        return simple_attack.use_cooldown_attack(
            state, self.cooldown_duration, self.damage, self.hit, self.delay
        )

    @reducer_method
    @ignore_rejected
    def use_with_ignore_reject(self, _: None, state: AttackSkillState):
        """
        This method is used to ignore the rejected event.
        Useful when automatic triggering is needed.
        """
        return simple_attack.use_cooldown_attack(
            state, self.cooldown_duration, self.damage, self.hit, self.delay
        )

    @reducer_method
    def reset_cooldown(self, _: None, state: AttackSkillState):
        return cooldown_trait.reset_cooldown(state)

    @view_method
    def validity(self, state: AttackSkillState):
        return cooldown_trait.validity_view(
            state, self.id, self.name, self.cooldown_duration
        )
