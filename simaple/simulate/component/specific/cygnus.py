from typing import Optional, TypedDict

import simaple.simulate.component.trait.consumable_trait as consumable_trait
import simaple.simulate.component.trait.lasting_trait as lasting_trait
from simaple.core.base import Stat
from simaple.simulate.component.base import Component, reducer_method, view_method
from simaple.simulate.component.entity import Consumable, Lasting
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class TranscendentCygnusBlessingState(TypedDict):
    lasting: Lasting
    dynamics: Dynamics
    consumable: Consumable


class TranscendentCygnusBlessingComponentProps(TypedDict):
    id: str
    name: str
    cooldown_duration: float
    delay: float
    lasting_duration: float
    damage_increment: float
    increase_interval: float
    default_damage: float
    maximum_damage: float
    maximum_stack: int


class TranscendentCygnusBlessing(
    Component,
):
    cooldown_duration: float
    delay: float
    lasting_duration: float

    damage_increment: float
    increase_interval: float
    default_damage: float
    maximum_damage: float
    maximum_stack: int

    def get_default_state(self) -> TranscendentCygnusBlessingState:
        return {
            "consumable": Consumable(
                time_left=self.cooldown_duration,
                cooldown_duration=self.cooldown_duration,
                maximum_stack=self.maximum_stack,
                stack=self.maximum_stack,
            ),
            "lasting": Lasting(time_left=0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> TranscendentCygnusBlessingComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
            "lasting_duration": self.lasting_duration,
            "damage_increment": self.damage_increment,
            "increase_interval": self.increase_interval,
            "default_damage": self.default_damage,
            "maximum_damage": self.maximum_damage,
            "maximum_stack": self.maximum_stack,
        }

    @reducer_method
    def use(self, _: None, state: TranscendentCygnusBlessingState):
        return consumable_trait.start_consumable_buff(
            state,
            {},
            **self.get_props(),
            apply_buff_duration=False,
        )

    @reducer_method
    def elapse(self, time: float, state: TranscendentCygnusBlessingState):
        return consumable_trait.elapse_consumable_buff(state, {"time": time})

    @view_method
    def validity(self, state: TranscendentCygnusBlessingState):
        return consumable_trait.consumable_validity(state, **self.get_props())

    @view_method
    def buff(self, state: TranscendentCygnusBlessingState) -> Optional[Stat]:
        if state["lasting"].enabled():
            return self.get_cygnus_buff_effect(state)

        return None

    @view_method
    def running(self, state: TranscendentCygnusBlessingState) -> Running:
        return lasting_trait.running_view(state, **self.get_props())

    def get_cygnus_buff_effect(self, state: TranscendentCygnusBlessingState) -> Stat:
        elapsed = state["lasting"].get_elapsed_time()
        tick_count = elapsed // self.increase_interval
        damage_multiplier = min(
            self.default_damage + self.damage_increment * tick_count,
            self.maximum_damage,
        )
        return Stat(damage_multiplier=damage_multiplier)
