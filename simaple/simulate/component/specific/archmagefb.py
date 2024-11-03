from typing import Optional, TypedDict

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.lasting_trait as lasting_trait
import simaple.simulate.component.trait.periodic_trait as periodic_trait
import simaple.simulate.component.trait.simple_attack as simple_attack
from simaple.core import Stat
from simaple.simulate.component.base import (
    Component,
    Event,
    reducer_method,
    view_method,
)
from simaple.simulate.component.entity import Cooldown, Lasting, Periodic, Stack
from simaple.simulate.component.util import is_rejected
from simaple.simulate.component.view import Running
from simaple.simulate.core.base import Entity
from simaple.simulate.event import EmptyEvent
from simaple.simulate.global_property import Dynamics


class FerventDrainStack(Entity):
    count: int
    max_count: int

    def set_max_count(self, max_count: int):
        self.max_count = max_count

    def get_count(self) -> int:
        return min(self.count, self.max_count)

    def set_count(self, count: int):
        self.count = count

    def get_buff(self) -> Stat:
        return Stat(final_damage_multiplier=self.get_count() * 5)


class FerventDrainState(TypedDict):
    drain_stack: FerventDrainStack


class FerventDrain(Component):
    cooldown_duration: float = 0
    delay: float = 0

    def get_default_state(self):
        return {
            "drain_stack": FerventDrainStack(count=5, max_count=5),
        }

    @view_method
    def buff(self, state: FerventDrainState) -> Stat:
        return state["drain_stack"].get_buff()

    @view_method
    def running(self, state: FerventDrainState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=999_999_999,
            lasting_duration=999_999_999,
        )


class PoisonNovaEntity(Entity):
    time_left: float
    maximum_time_left: float

    def create_nova(self, remaining_time):
        self.time_left = remaining_time

    def try_trigger_nova(self) -> bool:
        if 0 < self.time_left < self.maximum_time_left:
            self.time_left = 0
            return True

        return False

    def elapse(self, time: float):
        self.time_left -= time


class PoisonNovaState(TypedDict):
    cooldown: Cooldown
    poison_nova: PoisonNovaEntity
    dynamics: Dynamics


class PoisonNovaComponentProps(TypedDict):
    id: str
    name: str
    damage: float
    hit: float

    nova_remaining_time: float
    nova_damage: float
    nova_single_hit: int
    nova_hit_count: int

    dot_damage: float
    dot_lasting_duration: float

    cooldown_duration: float
    delay: float


class PoisonNovaComponent(Component):
    name: str
    damage: float
    hit: float

    nova_remaining_time: float
    nova_damage: float
    nova_single_hit: int
    nova_hit_count: int

    dot_damage: float
    dot_lasting_duration: float

    delay: float
    cooldown_duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "poison_nova": PoisonNovaEntity(
                time_left=0, maximum_time_left=100 * 1000.0
            ),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> PoisonNovaComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "damage": self.damage,
            "hit": self.hit,
            "nova_remaining_time": self.nova_remaining_time,
            "nova_damage": self.nova_damage,
            "nova_single_hit": self.nova_single_hit,
            "nova_hit_count": self.nova_hit_count,
            "dot_damage": self.dot_damage,
            "dot_lasting_duration": self.dot_lasting_duration,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
        }

    @reducer_method
    def elapse(self, time: float, state: PoisonNovaState):
        cooldown, poison_nova = (
            state["cooldown"].model_copy(),
            state["poison_nova"].model_copy(),
        )

        cooldown.elapse(time)
        poison_nova.elapse(time)
        state["cooldown"], state["poison_nova"] = cooldown, poison_nova

        return state, [EmptyEvent.elapsed(time)]

    @reducer_method
    def use(self, _: None, state: PoisonNovaState):
        if not state["cooldown"].available:
            return state, [EmptyEvent.rejected()]

        cooldown, poison_nova = (
            state["cooldown"].model_copy(),
            state["poison_nova"].model_copy(),
        )

        cooldown.set_time_left(
            state["dynamics"].stat.calculate_cooldown(self.cooldown_duration)
        )
        poison_nova.create_nova(self.nova_remaining_time)

        state["cooldown"], state["poison_nova"] = cooldown, poison_nova

        return state, [
            EmptyEvent.dealt(self.damage, self.hit),
            EmptyEvent.delayed(self.delay),
            simple_attack.get_dot_event(
                self.name, self.dot_damage, self.dot_lasting_duration
            ),
        ]

    @reducer_method
    def trigger(self, _: None, state: PoisonNovaState):
        poison_nova = state["poison_nova"].model_copy()

        triggered = poison_nova.try_trigger_nova()
        state["poison_nova"] = poison_nova

        if triggered:
            return state, [
                EmptyEvent.dealt(
                    self.nova_damage, self.nova_single_hit * min(self.nova_hit_count, 3)
                ),
                EmptyEvent.dealt(
                    self.nova_damage * 0.5,
                    self.nova_single_hit * max(self.nova_hit_count - 3, 0),
                ),
            ]

        return state, []

    @view_method
    def validity(self, state: PoisonNovaState):
        return cooldown_trait.validity_view(state, **self.get_props())


class PoisonChainState(TypedDict):
    cooldown: Cooldown
    periodic: Periodic
    stack: Stack
    dynamics: Dynamics


class PoisonChainComponentProps(TypedDict):
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

    periodic_damage_increment: float


class PoisonChainComponent(
    Component,
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

    periodic_damage_increment: float

    def get_default_state(self) -> PoisonChainState:
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(
                interval=self.periodic_interval,
                initial_counter=self.periodic_initial_delay,
                time_left=0,
            ),
            "stack": Stack(maximum_stack=5),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> PoisonChainComponentProps:
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
            "periodic_damage_increment": self.periodic_damage_increment,
        }

    def get_periodic_damage(self, stack: Stack):
        return self.periodic_damage + self.periodic_damage_increment * stack.get_stack()

    @reducer_method
    def elapse(self, time: float, state: PoisonChainState):
        cooldown, periodic, stack = (
            state["cooldown"].model_copy(),
            state["periodic"].model_copy(),
            state["stack"].model_copy(),
        )

        cooldown.elapse(time)

        dealing_events = []

        for _ in range(periodic.elapse(time)):
            dealing_events.append(
                EmptyEvent.dealt(self.get_periodic_damage(stack), self.periodic_hit)
            )
            stack.increase(1)

        state["cooldown"], state["periodic"], state["stack"] = cooldown, periodic, stack

        return state, [EmptyEvent.elapsed(time)] + dealing_events

    @reducer_method
    def use(self, _: None, state: PoisonChainState):
        state, events = periodic_trait.start_periodic_with_cooldown(
            state,
            {},
            **self.get_props(),
        )

        if not is_rejected(events):
            stack = state["stack"].model_copy()
            stack.reset(1)
            state["stack"] = stack

        return state, events

    @view_method
    def validity(self, state: PoisonChainState):
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def running(self, state: PoisonChainState) -> Running:
        return periodic_trait.running_view(
            state,
            **self.get_props(),
        )


class DotPunisherState(TypedDict):
    cooldown: Cooldown
    dynamics: Dynamics


class DotPunisherComponentProps(TypedDict):
    id: str
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    multiple: int

    dot_damage: float
    dot_lasting_duration: float


class DotPunisherComponent(Component):
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    multiple: int

    dot_damage: float
    dot_lasting_duration: float

    def get_default_state(self) -> DotPunisherState:
        return {
            "cooldown": Cooldown(time_left=0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> DotPunisherComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "damage": self.damage,
            "hit": self.hit,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
            "multiple": self.multiple,
            "dot_damage": self.dot_damage,
            "dot_lasting_duration": self.dot_lasting_duration,
        }

    @reducer_method
    def use(self, _: None, state: DotPunisherState):
        if not state["cooldown"].available:
            return state, [EmptyEvent.rejected()]

        cooldown = state["cooldown"].model_copy()
        cooldown.set_time_left(
            state["dynamics"].stat.calculate_cooldown(self.cooldown_duration)
        )
        state["cooldown"] = cooldown

        return state, [
            EmptyEvent.dealt(self.damage, self.hit) for _ in range(self.multiple)
        ] + [
            EmptyEvent.delayed(self.delay),
            simple_attack.get_dot_event(
                self.name, self.dot_damage, self.dot_lasting_duration
            ),
        ]

    @reducer_method
    def elapse(self, time: float, state: DotPunisherState):
        return cooldown_trait.elapse_cooldown_only(state, {"time": time})

    @reducer_method
    def reset_cooldown(self, _: None, state: DotPunisherState):
        cooldown = state["cooldown"].model_copy()
        cooldown.set_time_left(0)
        state["cooldown"] = cooldown

        return state, []

    @view_method
    def validity(self, state: DotPunisherState):
        return cooldown_trait.validity_view(state, **self.get_props())


class IfrittState(TypedDict):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class IfrittComponentProps(TypedDict):
    id: str
    name: str
    damage: float
    hit: float
    delay: float

    cooldown_duration: float

    periodic_initial_delay: Optional[float]
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float

    lasting_duration: float

    dot_damage: float
    dot_lasting_duration: float


class IfrittComponent(
    Component,
):
    name: str
    damage: float
    hit: float
    delay: float

    cooldown_duration: float

    periodic_initial_delay: Optional[float] = None
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float

    lasting_duration: float

    dot_damage: float
    dot_lasting_duration: float

    def get_default_state(self) -> IfrittState:
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(
                interval=self.periodic_interval,
                initial_counter=self.periodic_initial_delay,
                time_left=0,
            ),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> IfrittComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "damage": self.damage,
            "hit": self.hit,
            "delay": self.delay,
            "cooldown_duration": self.cooldown_duration,
            "periodic_initial_delay": self.periodic_initial_delay,
            "periodic_interval": self.periodic_interval,
            "periodic_damage": self.periodic_damage,
            "periodic_hit": self.periodic_hit,
            "lasting_duration": self.lasting_duration,
            "dot_damage": self.dot_damage,
            "dot_lasting_duration": self.dot_lasting_duration,
        }

    @reducer_method
    def elapse(self, time: float, state: IfrittState):
        return periodic_trait.elapse_periodic_with_cooldown(
            state, {"time": time}, **self.get_props()
        )

    @reducer_method
    def use(self, _: None, state: IfrittState):
        state, event = periodic_trait.start_periodic_with_cooldown(
            state,
            {},
            **self.get_props(),
        )
        return state, event + [
            simple_attack.get_dot_event(
                self.name, self.dot_damage, self.dot_lasting_duration
            )
        ]

    @view_method
    def validity(self, state: IfrittState):
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def running(self, state: IfrittState) -> Running:
        return periodic_trait.running_view(
            state,
            **self.get_props(),
        )


class InfernalVenomState(TypedDict):
    drain_stack: FerventDrainStack
    cooldown: Cooldown
    dynamics: Dynamics
    lasting: Lasting


class InfernalVenomComponentProps(TypedDict):
    id: str
    name: str
    first_damage: float
    first_hit: float
    second_damage: float
    second_hit: float
    cooldown_duration: float
    delay: float
    lasting_duration: float


class InfernalVenom(
    Component,
):
    first_damage: float
    first_hit: float

    second_damage: float
    second_hit: float

    cooldown_duration: float
    delay: float
    lasting_duration: float

    def get_default_state(self) -> InfernalVenomState:
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
            "drain_stack": FerventDrainStack(count=5, max_count=5),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> InfernalVenomComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "first_damage": self.first_damage,
            "first_hit": self.first_hit,
            "second_damage": self.second_damage,
            "second_hit": self.second_hit,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
            "lasting_duration": self.lasting_duration,
        }

    @reducer_method
    def use(self, _: None, state: InfernalVenomState):
        if not state["cooldown"].available:
            return state, [EmptyEvent.rejected()]

        cooldown, lasting, drain_stack = (
            state["cooldown"].model_copy(),
            state["lasting"].model_copy(),
            state["drain_stack"].model_copy(),
        )
        cooldown.set_time_left(
            state["dynamics"].stat.calculate_cooldown(self.cooldown_duration)
        )

        drain_stack.set_max_count(10)
        drain_stack.set_count(10)
        lasting.set_time_left(self.lasting_duration)

        state["cooldown"], state["lasting"], state["drain_stack"] = (
            cooldown,
            lasting,
            drain_stack,
        )

        return state, [
            EmptyEvent.dealt(self.first_damage, self.first_hit),
            EmptyEvent.dealt(self.second_damage, self.second_hit),
            EmptyEvent.delayed(self.delay),
        ]

    @reducer_method
    def elapse(
        self, time: float, state: InfernalVenomState
    ) -> tuple[InfernalVenomState, list[Event]]:
        cooldown, lasting, drain_stack = (
            state["cooldown"].model_copy(),
            state["lasting"].model_copy(),
            state["drain_stack"].model_copy(),
        )

        was_enabled = lasting.enabled()

        cooldown.elapse(time)
        lasting.elapse(time)

        if not lasting.enabled() and was_enabled:
            drain_stack.set_max_count(5)
            drain_stack.set_count(5)

        state["cooldown"], state["lasting"], state["drain_stack"] = (
            cooldown,
            lasting,
            drain_stack,
        )

        return state, [
            EmptyEvent.elapsed(time),
        ]

    @view_method
    def validity(self, state: InfernalVenomState):
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def running(self, state: InfernalVenomState) -> Running:
        return lasting_trait.running_view(state, **self.get_props())


class FlameSwipVIState(TypedDict):
    cooldown: Cooldown
    dynamics: Dynamics
    stack: Stack


class FlameSwipVIComponentProps(TypedDict):
    id: str
    name: str
    delay: float
    damage: float
    hit: int
    cooldown_duration: float
    explode_damage: float
    explode_hit: int
    dot_damage: float
    dot_lasting_duration: float


class FlameSwipVI(
    Component,
):
    delay: float
    damage: float
    hit: int
    cooldown_duration: float

    explode_damage: float
    explode_hit: int

    dot_damage: float
    dot_lasting_duration: float

    def get_default_state(self) -> FlameSwipVIState:
        return {
            "cooldown": Cooldown(time_left=0),
            "stack": Stack(maximum_stack=3),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> FlameSwipVIComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "delay": self.delay,
            "damage": self.damage,
            "hit": self.hit,
            "cooldown_duration": self.cooldown_duration,
            "explode_damage": self.explode_damage,
            "explode_hit": self.explode_hit,
            "dot_damage": self.dot_damage,
            "dot_lasting_duration": self.dot_lasting_duration,
        }

    @reducer_method
    def use(self, _: None, state: FlameSwipVIState):
        state, event = simple_attack.use_cooldown_attack(
            state,
            {},
            **self.get_props(),
        )

        event += [
            simple_attack.get_dot_event(
                self.name, self.dot_damage, self.dot_lasting_duration
            )
        ]

        stack = state["stack"].model_copy()
        stack.increase(1)
        state["stack"] = stack

        return state, event

    @reducer_method
    def explode(self, _: None, state: FlameSwipVIState):
        if state["stack"].get_stack() < 3:
            return state, []

        stack = state["stack"].model_copy()
        stack.reset(0)
        state["stack"] = stack

        return state, [
            EmptyEvent.dealt(self.explode_damage, self.explode_hit),
        ]

    @view_method
    def validity(self, state: FlameSwipVIState):
        return cooldown_trait.validity_view(state, **self.get_props())
