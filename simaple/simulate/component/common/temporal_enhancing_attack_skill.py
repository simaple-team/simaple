from typing import TypedDict

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.entity import Cooldown
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.event import EmptyEvent
from simaple.simulate.global_property import Dynamics


class TemporalEnhancingAttackSkillState(TypedDict):
    cooldown: Cooldown
    reforged_cooldown: Cooldown
    dynamics: Dynamics


class TemporalEnhancingAttackSkillComponentProps(TypedDict):
    id: str
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float
    reforged_damage: float
    reforged_hit: float
    reforged_multiple: int
    reforge_cooldown_duration: float


class TemporalEnhancingAttackSkill(
    SkillComponent,
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

    def get_default_state(self) -> TemporalEnhancingAttackSkillState:
        return {
            "cooldown": Cooldown(time_left=0),
            "reforged_cooldown": Cooldown(time_left=0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> TemporalEnhancingAttackSkillComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "damage": self.damage,
            "hit": self.hit,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
            "reforged_damage": self.reforged_damage,
            "reforged_hit": self.reforged_hit,
            "reforged_multiple": self.reforged_multiple,
            "reforge_cooldown_duration": self.reforge_cooldown_duration,
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: TemporalEnhancingAttackSkillState,
    ):
        if not state["cooldown"].available:
            return state, [EmptyEvent.rejected()]

        cooldown, reforged_cooldown = (
            state["cooldown"].model_copy(),
            state["reforged_cooldown"].model_copy(),
        )

        cooldown.set_time_left(
            state["dynamics"].stat.calculate_cooldown(self.cooldown_duration)
        )

        damage_events = [EmptyEvent.dealt(self.damage, self.hit)]

        if reforged_cooldown.available:
            damage_events = [
                EmptyEvent.dealt(self.reforged_damage, self.reforged_hit)
                for _ in range(self.reforged_multiple)
            ]
            reforged_cooldown.set_time_left(
                state["dynamics"].stat.calculate_cooldown(
                    self.reforge_cooldown_duration
                )
            )

        state["cooldown"] = cooldown
        state["reforged_cooldown"] = reforged_cooldown

        return state, damage_events + [
            EmptyEvent.delayed(self.delay),
        ]

    @reducer_method
    def elapse(self, time: float, state: TemporalEnhancingAttackSkillState):
        cooldown, reforged_cooldown = (
            state["cooldown"].model_copy(),
            state["reforged_cooldown"].model_copy(),
        )
        cooldown.elapse(time)
        reforged_cooldown.elapse(time)

        state["cooldown"] = cooldown
        state["reforged_cooldown"] = reforged_cooldown

        return state, [EmptyEvent.elapsed(time)]

    @view_method
    def validity(self, state: TemporalEnhancingAttackSkillState):
        return cooldown_trait.validity_view(state, **self.get_props())
