from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.component.base import Component, reducer_method, view_method
from simaple.simulate.component.skill import (
    AttackSkillComponent,
    CooldownState,
    StackState,
)
from simaple.simulate.global_property import Dynamics


def use_frost_stack(frost_effect: StackState) -> tuple[StackState, Optional[Stat]]:
    if frost_effect.stack == 0:
        return frost_effect, None

    new_frost_effect = frost_effect
    effect_count = new_frost_effect.stack
    new_frost_effect.decrease(1)
    return new_frost_effect, Stat(damage_multiplier=effect_count * 12)  # Magic Number


class FrostEffect(Component):
    name: str = "프로스트 이펙트"
    critical_damage_per_stack: int
    maximum_stack: int

    def get_default_state(self):
        return {"frost_stack": StackState(maximum_stack=self.maximum_stack)}

    @reducer_method
    def increase_step(self, _: None, frost_stack: StackState):
        frost_stack = frost_stack.copy()
        frost_stack.increase(1)
        return frost_stack, []

    @view_method
    def buff(self, frost_stack: StackState):
        return Stat(critical_damage=self.critical_damage_per_stack * frost_stack.stack)

    @view_method
    def stack(self, frost_stack: StackState):
        return frost_stack.get_stack()


class ThunderAttackSkillComponent(AttackSkillComponent):
    binds: dict[str, str] = {"frost_stack": ".프로스트 이펙트.frost_stack"}

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        frost_stack: StackState,
        dynamics: Dynamics,
    ):
        cooldown_state = cooldown_state.copy()

        if not cooldown_state.available:
            return cooldown_state, self.event_provider.rejected()

        cooldown_state.set_time_left(dynamics.stat.calculate_cooldown(self.cooldown))

        frost_stack, modifier = use_frost_stack(frost_stack)

        return (cooldown_state, frost_stack, dynamics), [
            self.event_provider.dealt(self.damage, self.hit, modifier=modifier),
            self.event_provider.delayed(self.delay),
        ]
