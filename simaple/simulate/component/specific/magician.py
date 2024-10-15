from typing import Optional, TypedDict

import simaple.simulate.component.trait.common.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.common.lasting_trait as lasting_trait
from simaple.core.base import Stat
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Lasting
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class InfinityState(TypedDict):
    cooldown: Cooldown
    lasting: Lasting
    dynamics: Dynamics


class Infinity(SkillComponent):
    cooldown_duration: float
    delay: float
    lasting_duration: float

    final_damage_increment: float
    increase_interval: float
    default_final_damage: float
    maximum_final_damage: float

    apply_buff_duration: bool = True

    def get_default_state(self) -> InfinityState:
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    @reducer_method
    def use(self, _: None, state: InfinityState):
        return lasting_trait.start_lasting_with_cooldown(
            state,
            self.cooldown_duration,
            self.lasting_duration,
            self.delay,
            apply_buff_duration=self.apply_buff_duration,
        )

    @reducer_method
    def elapse(self, time: float, state: InfinityState):
        return lasting_trait.elapse_lasting_with_cooldown(state, time)

    @view_method
    def validity(self, state: InfinityState):
        return cooldown_trait.validity_view(
            state,
            self.id,
            self.name,
            self.cooldown_duration,
        )

    @view_method
    def buff(self, state: InfinityState) -> Optional[Stat]:
        if state["lasting"].enabled():
            return self.get_infinity_effect(state)

        return None

    @view_method
    def running(self, state: InfinityState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state["lasting"].time_left,
            lasting_duration=state["lasting"].assigned_duration,
        )

    def get_infinity_effect(self, state: InfinityState) -> Stat:
        elapsed = state["lasting"].get_elapsed_time()
        tick_count = elapsed // self.increase_interval
        final_damage_multiplier = min(
            self.default_final_damage + self.final_damage_increment * tick_count,
            self.maximum_final_damage,
        )
        return Stat(final_damage_multiplier=final_damage_multiplier)
