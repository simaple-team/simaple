from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown
from simaple.simulate.component.feature import DamageAndHit
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import InvalidatableCooldownTrait
from simaple.simulate.global_property import Dynamics


class MultipleHitHexaSkillState(ReducerState):
    cooldown: Cooldown
    dynamics: Dynamics


class MultipleHitHexaSkillComponent(
    SkillComponent,
    InvalidatableCooldownTrait,
):
    """
    MultipleHitHexaSkillComponent
    This describes skill that act like:
    - various Initial damage x hit
    """

    name: str
    damage_and_hits: list[DamageAndHit]
    delay: float

    cooldown_duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, state: MultipleHitHexaSkillState):
        state = state.deepcopy()
        state.cooldown.elapse(time)
        return state, [self.event_provider.elapsed(time)]

    @reducer_method
    def use(self, _: None, state: MultipleHitHexaSkillState):
        if not state.cooldown.available:
            return state, [self.event_provider.rejected()]

        state = state.deepcopy()

        delay = self._get_delay()

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown_duration())
        )

        return state, [
            self.event_provider.dealt(entry.damage, entry.hit)
            for entry in self.damage_and_hits
        ] + [
            self.event_provider.delayed(delay),
        ]

    @view_method
    def validity(self, state: MultipleHitHexaSkillState):
        return self.validity_in_invalidatable_cooldown_trait(state)
