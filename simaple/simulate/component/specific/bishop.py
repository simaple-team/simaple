from typing import Optional, TypedDict

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.periodic_trait as periodic_trait
import simaple.simulate.component.trait.simple_attack as simple_attack
from simaple.core.base import Stat
from simaple.simulate.component.base import reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Periodic, Stack
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.view import Running
from simaple.simulate.core.base import Entity
from simaple.simulate.event import EmptyEvent
from simaple.simulate.global_property import Dynamics


class DivineMark(Entity):
    advantage: Optional[Stat] = None

    def mark(self, advantage: Stat):
        self.advantage = advantage

    def consume_mark(self) -> Stat:
        self.advantage, advantage = None, self.advantage
        if advantage is None:
            advantage = Stat()

        return advantage


class DivineAttackSkillState(TypedDict):
    divine_mark: DivineMark
    cooldown: Cooldown
    dynamics: Dynamics


class DivineAttackSkillComponentProps(TypedDict):
    id: str
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float
    synergy: Optional[Stat]


class DivineAttackSkillComponent(
    SkillComponent,
):
    binds: dict[str, str] = {
        "divine_mark": ".바하뮤트.divine_mark",
    }
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float
    synergy: Optional[Stat] = None

    def get_default_state(self) -> DivineAttackSkillState:
        return {
            "cooldown": Cooldown(time_left=0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
            "divine_mark": DivineMark(),
        }

    def get_props(self) -> DivineAttackSkillComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "damage": self.damage,
            "hit": self.hit,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
            "synergy": self.synergy,
        }

    @reducer_method
    def use(self, _: None, state: DivineAttackSkillState):
        if not state["cooldown"].available:
            return state, [EmptyEvent.rejected()]

        cooldown, divine_mark = (
            state["cooldown"].model_copy(),
            state["divine_mark"].model_copy(),
        )

        cooldown.set_time_left(
            state["dynamics"].stat.calculate_cooldown(self.cooldown_duration)
        )

        modifier = divine_mark.consume_mark()

        state["cooldown"] = cooldown
        state["divine_mark"] = divine_mark

        return state, [
            EmptyEvent.dealt(self.damage, self.hit, modifier=modifier),
            EmptyEvent.delayed(self.delay),
        ]

    @reducer_method
    def elapse(self, time: float, state: DivineAttackSkillState):
        return simple_attack.elapse(state, time)

    @view_method
    def validity(self, state: DivineAttackSkillState):
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def buff(self, _: DivineAttackSkillState):
        return self.synergy


class DivineMinionState(TypedDict):
    divine_mark: DivineMark
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class DivineMinionComponentProps(TypedDict):
    id: str
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float
    periodic_initial_delay: Optional[float]
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float
    mark_advantage: Stat
    stat: Optional[Stat]


class DivineMinion(
    SkillComponent,
):
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    periodic_initial_delay: Optional[float] = None
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float

    mark_advantage: Stat
    stat: Optional[Stat] = None

    def get_default_state(self) -> DivineMinionState:
        if self.name == "바하뮤트":
            return {
                "divine_mark": DivineMark(),
                "cooldown": Cooldown(time_left=0),
                "periodic": Periodic(
                    interval=self.periodic_interval,
                    initial_counter=self.periodic_initial_delay,
                    time_left=0,
                ),
                "dynamics": Dynamics.model_validate({"stat": {}}),
            }

        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(
                interval=self.periodic_interval,
                initial_counter=self.periodic_initial_delay,
                time_left=0,
            ),
            "dynamics": Dynamics.model_validate({"stat": {}}),
            "divine_mark": DivineMark(),
        }

    def get_props(self) -> DivineMinionComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "damage": self.damage,
            "hit": self.hit,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
            "periodic_initial_delay": self.periodic_initial_delay,
            "periodic_interval": self.periodic_interval,
            "periodic_damage": self.periodic_damage,
            "periodic_hit": self.periodic_hit,
            "lasting_duration": self.lasting_duration,
            "mark_advantage": self.mark_advantage,
            "stat": self.stat,
        }

    @reducer_method
    def elapse(self, time: float, state: DivineMinionState):
        cooldown, periodic, divine_mark = (
            state["cooldown"].model_copy(),
            state["periodic"].model_copy(),
            state["divine_mark"].model_copy(),
        )

        cooldown.elapse(time)
        dealing_events = []

        for _ in range(periodic.elapse(time)):
            divine_mark.mark(self.mark_advantage)
            dealing_events.append(
                EmptyEvent.dealt(
                    self.periodic_damage,
                    self.periodic_hit,
                )
            )

        state["cooldown"] = cooldown
        state["periodic"] = periodic
        state["divine_mark"] = divine_mark

        return state, [EmptyEvent.elapsed(time)] + dealing_events

    @view_method
    def buff(self, state: DivineMinionState):
        if state["periodic"].enabled():
            return self.stat

        return None

    @reducer_method
    def use(self, _: None, state: DivineMinionState):
        return periodic_trait.start_periodic_with_cooldown(
            state,
            self.damage,
            self.hit,
            self.delay,
            self.cooldown_duration,
            self.lasting_duration,
        )

    @view_method
    def validity(self, state: DivineMinionState):
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def running(self, state: DivineMinionState) -> Running:
        return periodic_trait.running_view(
            state, self.id, self.name, self.lasting_duration
        )


class HexaAngelRayState(TypedDict):
    divine_mark: DivineMark
    cooldown: Cooldown
    dynamics: Dynamics
    punishing_stack: Stack


class HexaAngelRayComponentProps(TypedDict):
    id: str
    name: str
    damage: float
    hit: float
    delay: float
    punishing_damage: float
    punishing_hit: float
    stack_resolve_amount: int
    synergy: Stat
    cooldown_duration: float


class HexaAngelRayComponent(
    SkillComponent,
):
    binds: dict[str, str] = {
        "divine_mark": ".바하뮤트.divine_mark",
    }
    name: str
    damage: float
    hit: float
    delay: float

    punishing_damage: float
    punishing_hit: float
    stack_resolve_amount: int

    synergy: Stat

    def get_default_state(self) -> HexaAngelRayState:
        return {
            "cooldown": Cooldown(time_left=0),
            "punishing_stack": Stack(
                maximum_stack=self.stack_resolve_amount * 2 - 1
            ),  # one-buffer
            "dynamics": Dynamics.model_validate({"stat": {}}),
            "divine_mark": DivineMark(),
        }

    def get_props(self) -> HexaAngelRayComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "damage": self.damage,
            "hit": self.hit,
            "delay": self.delay,
            "punishing_damage": self.punishing_damage,
            "punishing_hit": self.punishing_hit,
            "stack_resolve_amount": self.stack_resolve_amount,
            "synergy": self.synergy,
            "cooldown_duration": self.cooldown_duration,
        }

    @reducer_method
    def use(self, _: None, state: HexaAngelRayState):
        if not state["cooldown"].available:
            return state, [EmptyEvent.rejected()]

        cooldown, divine_mark = (
            state["cooldown"].model_copy(),
            state["divine_mark"].model_copy(),
        )

        cooldown.set_time_left(
            state["dynamics"].stat.calculate_cooldown(self.cooldown_duration)
        )

        modifier = divine_mark.consume_mark()

        state["cooldown"] = cooldown
        state["divine_mark"] = divine_mark
        state, stack_events = self._stack(state)

        return (
            state,
            [
                EmptyEvent.dealt(self.damage, self.hit, modifier=modifier),
                EmptyEvent.delayed(self.delay),
            ]
            + stack_events,
        )

    @reducer_method
    def stack(self, _: None, state: HexaAngelRayState):
        return self._stack(state)

    def _stack(self, state: HexaAngelRayState):
        """
        Add 1 stack for Holy Punishing.

        This method can be called internally, or
        can be called by Divine Punishmenet.
        """
        punish_stack = state["punishing_stack"].model_copy()

        punish_stack.increase(1)
        if punish_stack.get_stack() >= self.stack_resolve_amount:
            punish_stack.decrease(self.stack_resolve_amount)
            state["punishing_stack"] = punish_stack

            return state, [EmptyEvent.dealt(self.punishing_damage, self.punishing_hit)]

        state["punishing_stack"] = punish_stack

        return state, []

    @reducer_method
    def elapse(self, time: float, state: HexaAngelRayState):
        return simple_attack.elapse(state, time)

    @view_method
    def validity(self, state: HexaAngelRayState):
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def buff(self, _: HexaAngelRayState):
        return self.synergy
