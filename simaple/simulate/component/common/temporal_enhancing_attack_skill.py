from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import InvalidatableCooldownTrait
from simaple.simulate.global_property import Dynamics


class TemporalEnhancingAttackSkillState(ReducerState):
    cooldown: Cooldown
    reforged_cooldown: Cooldown
    dynamics: Dynamics


class TemporalEnhancingAttackSkill(
    SkillComponent,
    InvalidatableCooldownTrait,
):
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    reforged_damage: float
    reforged_hit: float
    reforged_multiple: int

    reforge_cooldown_duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "reforged_cooldown": Cooldown(time_left=0),
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: TemporalEnhancingAttackSkillState,
    ):
        state = state.deepcopy()

        if not state.cooldown.available:
            return state, [self.event_provider.rejected()]

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self.cooldown_duration)
        )

        damage_events = [self.event_provider.dealt(self.damage, self.hit)]

        if state.reforged_cooldown.available:
            damage_events = [
                self.event_provider.dealt(self.reforged_damage, self.reforged_hit)
                for _ in range(self.reforged_multiple)
            ]
            state.reforged_cooldown.set_time_left(
                state.dynamics.stat.calculate_cooldown(self.reforge_cooldown_duration)
            )

        return state, damage_events + [
            self.event_provider.delayed(self.delay),
        ]

    @reducer_method
    def elapse(self, time: float, state: TemporalEnhancingAttackSkillState):
        state = state.deepcopy()
        state.cooldown.elapse(time)
        state.reforged_cooldown.elapse(time)
        return state, [self.event_provider.elapsed(time)]

    @view_method
    def validity(self, state: TemporalEnhancingAttackSkillState):
        return self.validity_in_invalidatable_cooldown_trait(state)
