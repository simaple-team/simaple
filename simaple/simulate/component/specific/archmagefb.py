from simaple.core import Stat
from simaple.simulate.base import Entity
from simaple.simulate.component.base import (
    Component,
    Event,
    ReducerState,
    reducer_method,
    view_method,
)
from simaple.simulate.component.entity import Cooldown, Lasting, Periodic, Stack
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import (
    AddDOTDamageTrait,
    BuffTrait,
    CooldownValidityTrait,
    PeriodicWithSimpleDamageTrait,
    UseSimpleAttackTrait,
)
from simaple.simulate.component.util import is_rejected
from simaple.simulate.component.view import Running, Validity
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


class FerventDrainState(ReducerState):
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
        return state.drain_stack.get_buff()

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


class PoisonNovaState(ReducerState):
    cooldown: Cooldown
    poison_nova: PoisonNovaEntity
    dynamics: Dynamics


class PoisonNovaComponent(SkillComponent, AddDOTDamageTrait):
    name: str
    damage: float
    hit: float

    nova_remaining_time: float
    nova_damage: float
    nova_single_hit: int
    nova_hit_count: int

    dot_damage: float
    dot_lasting_duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "poison_nova": PoisonNovaEntity(
                time_left=0, maximum_time_left=100 * 1000.0
            ),
        }

    @reducer_method
    def elapse(self, time: float, state: PoisonNovaState):
        state = state.deepcopy()
        state.cooldown.elapse(time)
        state.poison_nova.elapse(time)
        return state, self.event_provider.elapsed(time)

    @reducer_method
    def use(self, _: None, state: PoisonNovaState):
        state = state.deepcopy()

        if not state.cooldown.available:
            return state, self.event_provider.rejected()

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self.cooldown_duration)
        )
        state.poison_nova.create_nova(self.nova_remaining_time)

        return state, [
            self.event_provider.dealt(self.damage, self.hit),
            self.event_provider.delayed(self.delay),
            self.get_dot_add_event(),
        ]

    @reducer_method
    def trigger(self, _: None, state: PoisonNovaState):
        state = state.deepcopy()

        triggered = state.poison_nova.try_trigger_nova()
        if triggered:
            return state, [
                self.event_provider.dealt(
                    self.nova_damage, self.nova_single_hit * min(self.nova_hit_count, 3)
                ),
                self.event_provider.dealt(
                    self.nova_damage * 0.5,
                    self.nova_single_hit * max(self.nova_hit_count - 3, 0),
                ),
            ]

        return state, None

    @view_method
    def validity(self, state: PoisonNovaState):
        return Validity(
            id=self.id,
            name=self.name,
            time_left=state.cooldown.minimum_time_to_available(),
            valid=state.cooldown.available,
            cooldown_duration=self.cooldown_duration,
        )

    def _get_dot_damage_and_lasting(self) -> tuple[float, float]:
        return self.dot_damage, self.dot_lasting_duration


class PoisonChainState(ReducerState):
    cooldown: Cooldown
    periodic: Periodic
    stack: Stack
    dynamics: Dynamics


class PoisonChainComponent(
    SkillComponent, PeriodicWithSimpleDamageTrait, CooldownValidityTrait
):
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float

    periodic_damage_increment: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(interval=self.periodic_interval, time_left=0),
            "stack": Stack(maximum_stack=5),
        }

    def get_periodic_damage(self, state: PoisonChainState):
        return (
            self.periodic_damage
            + self.periodic_damage_increment * state.stack.get_stack()
        )

    @reducer_method
    def elapse(self, time: float, state: PoisonChainState):
        state = state.deepcopy()

        state.cooldown.elapse(time)

        dealing_events = []

        for _ in state.periodic.resolving(time):
            dealing_events.append(
                self.event_provider.dealt(
                    self.get_periodic_damage(state), self.periodic_hit
                )
            )
            state.stack.increase(1)

        return state, [self.event_provider.elapsed(time)] + dealing_events

    @reducer_method
    def use(self, _: None, state: PoisonChainState):
        state = state.deepcopy()

        state, events = self.use_periodic_damage_trait(state)
        if not is_rejected(events):
            state.stack.reset(1)

        return state, events

    @view_method
    def validity(self, state: PoisonChainState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def running(self, state: PoisonChainState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state.periodic.time_left,
            lasting_duration=self._get_lasting_duration(state),
        )

    def _get_lasting_duration(self, state: PoisonChainState) -> float:
        return self.lasting_duration

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit

    def _get_periodic_damage_hit(self, state: PoisonChainState) -> tuple[float, float]:
        return self.periodic_damage, self.periodic_hit


class DotPunisherState(ReducerState):
    cooldown: Cooldown
    dynamics: Dynamics


class DotPunisherComponent(SkillComponent, CooldownValidityTrait, AddDOTDamageTrait):
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    multiple: int

    dot_damage: float
    dot_lasting_duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
        }

    @reducer_method
    def use(self, _: None, state: DotPunisherState):
        state = state.deepcopy()

        if not state.cooldown.available:
            return state, self.event_provider.rejected()

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self.cooldown_duration)
        )

        return state, [
            self.event_provider.dealt(self.damage, self.hit)
            for _ in range(self.multiple)
        ] + [self.event_provider.delayed(self.delay), self.get_dot_add_event()]

    @reducer_method
    def elapse(self, time: float, state: DotPunisherState):
        state = state.deepcopy()
        state.cooldown.elapse(time)
        return state, [self.event_provider.elapsed(time)]

    @reducer_method
    def reset_cooldown(self, _: None, state: DotPunisherState):
        state = state.deepcopy()
        state.cooldown.set_time_left(0)
        return state, None

    @view_method
    def validity(self, state: DotPunisherState):
        return self.validity_in_cooldown_trait(state)

    def _get_dot_damage_and_lasting(self) -> tuple[float, float]:
        return self.dot_damage, self.dot_lasting_duration


class IfrittState(ReducerState):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class IfrittComponent(
    SkillComponent,
    PeriodicWithSimpleDamageTrait,
    CooldownValidityTrait,
    AddDOTDamageTrait,
):
    name: str
    damage: float
    hit: float
    delay: float

    cooldown_duration: float

    periodic_interval: float
    periodic_damage: float
    periodic_hit: float

    lasting_duration: float

    dot_damage: float
    dot_lasting_duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(interval=self.periodic_interval, time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, state: IfrittState):
        return self.elapse_periodic_damage_trait(time, state)

    @reducer_method
    def use(self, _: None, state: IfrittState):
        state, event = self.use_periodic_damage_trait(state)
        return state, event + [self.get_dot_add_event()]

    @view_method
    def validity(self, state: IfrittState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def running(self, state: IfrittState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state.periodic.time_left,
            lasting_duration=self._get_lasting_duration(state),
        )

    def _get_lasting_duration(self, state: IfrittState) -> float:
        return self.lasting_duration

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit

    def _get_periodic_damage_hit(self, state: IfrittState) -> tuple[float, float]:
        return self.periodic_damage, self.periodic_hit

    def _get_dot_damage_and_lasting(self) -> tuple[float, float]:
        return self.dot_damage, self.dot_lasting_duration


class InfernalVenomState(ReducerState):
    drain_stack: FerventDrainStack
    cooldown: Cooldown
    dynamics: Dynamics
    lasting: Lasting


class InfernalVenom(
    SkillComponent,
    CooldownValidityTrait,
    BuffTrait,
):
    first_damage: float
    first_hit: float

    second_damage: float
    second_hit: float

    cooldown_duration: float
    delay: float
    lasting_duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
        }

    @reducer_method
    def use(self, _: None, state: InfernalVenomState):
        state = state.deepcopy()

        if not state.cooldown.available:
            return state, [self.event_provider.rejected()]

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self.cooldown_duration)
        )

        state.drain_stack.set_max_count(10)
        state.drain_stack.set_count(10)
        state.lasting.set_time_left(self.lasting_duration)

        return state, [
            self.event_provider.dealt(self.first_damage, self.first_hit),
            self.event_provider.dealt(self.second_damage, self.second_hit),
            self.event_provider.delayed(self.delay),
        ]

    @reducer_method
    def elapse(
        self, time: float, state: InfernalVenomState
    ) -> tuple[InfernalVenomState, list[Event]]:
        state = state.deepcopy()

        was_enabled = state.lasting.enabled()

        state.cooldown.elapse(time)
        state.lasting.elapse(time)

        if not state.lasting.enabled() and was_enabled:
            state.drain_stack.set_max_count(5)
            state.drain_stack.set_count(5)

        return state, [
            self.event_provider.elapsed(time),
        ]

    @view_method
    def validity(self, state: InfernalVenomState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def running(self, state: InfernalVenomState) -> Running:
        return self.running_in_buff_trait(state)

    def _get_lasting_duration(self, state: InfernalVenomState) -> float:
        return self.lasting_duration

    def _get_cooldown_duration(self) -> float:
        return self.cooldown_duration


class FlameSwipVIState(ReducerState):
    cooldown: Cooldown
    dynamics: Dynamics
    stack: Stack


class FlameSwipVI(
    SkillComponent, UseSimpleAttackTrait, AddDOTDamageTrait, CooldownValidityTrait
):
    delay: float
    damage: float
    hit: int
    cooldown_duration: float

    explode_damage: float
    explode_hit: int

    dot_damage: float
    dot_lasting_duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "stack": Stack(maximum_stack=3),
        }

    @reducer_method
    def use(self, _: None, state: FlameSwipVIState):
        state, event = self.use_simple_attack(state)
        event += [self.get_dot_add_event()]
        state.stack.increase(1)

        return state, event

    @reducer_method
    def explode(self, _: None, state: FlameSwipVIState):
        if state.stack.get_stack() < 3:
            return state, []

        state = state.deepcopy()
        state.stack.reset(0)

        return state, [
            self.event_provider.dealt(self.explode_damage, self.explode_hit),
        ]

    @view_method
    def validity(self, state: FlameSwipVIState):
        return self.validity_in_cooldown_trait(state)

    def _get_dot_damage_and_lasting(self) -> tuple[float, float]:
        return self.dot_damage, self.dot_lasting_duration

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit
