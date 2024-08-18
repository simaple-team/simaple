from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Lasting
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import BuffTrait, InvalidatableCooldownTrait
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class SynergyState(ReducerState):
    cooldown: Cooldown
    lasting: Lasting
    dynamics: Dynamics


class SynergySkillComponent(SkillComponent, BuffTrait, InvalidatableCooldownTrait):
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    synergy: Stat
    lasting_duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
        }

    @reducer_method
    def use(self, _: None, state: SynergyState):
        state = state.deepcopy()
        if not state.cooldown.available:
            return state, [self.event_provider.rejected()]

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self.cooldown_duration)
        )
        state.lasting.set_time_left(
            self.lasting_duration
        )  # note that synergy do not works with dynamic duration.

        return state, [
            self.event_provider.dealt(self.damage, self.hit),
            self.event_provider.delayed(self.delay),
        ]

    @reducer_method
    def elapse(self, time: float, state: SynergyState):
        return self.elapse_buff_trait(time, state)

    @view_method
    def validity(self, state: SynergyState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    @view_method
    def buff(self, state: SynergyState) -> Optional[Stat]:
        if state.lasting.enabled():
            return self.synergy

        return Stat()

    @view_method
    def running(self, state: SynergyState) -> Running:
        return self.running_in_buff_trait(state)

    def _get_lasting_duration(self, state: SynergyState) -> float:
        return self.lasting_duration


class AttackSkillIncludeReforgedState(ReducerState):
    cooldown: Cooldown
    reforged_cooldown: Cooldown
    dynamics: Dynamics


class AttackSkillIncludeReforged(
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
        state: AttackSkillIncludeReforgedState,
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
    def elapse(self, time: float, state: AttackSkillIncludeReforgedState):
        state = state.deepcopy()
        state.cooldown.elapse(time)
        state.reforged_cooldown.elapse(time)
        return state, [self.event_provider.elapsed(time)]

    @view_method
    def validity(self, state: AttackSkillIncludeReforgedState):
        return self.validity_in_invalidatable_cooldown_trait(state)
