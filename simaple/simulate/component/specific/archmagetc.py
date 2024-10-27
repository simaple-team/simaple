from typing import Optional, TypedDict

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.periodic_trait as periodic_trait
import simaple.simulate.component.trait.simple_attack as simple_attack
from simaple.core.base import Stat
from simaple.simulate.component.base import Component, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Periodic, Stack
from simaple.simulate.component.view import Running
from simaple.simulate.core.base import Entity
from simaple.simulate.event import EmptyEvent
from simaple.simulate.global_property import Dynamics


def get_frost_modifier(frost_effect: Stack) -> Stat:
    return Stat(damage_multiplier=frost_effect.stack * 12)  # Magic Number


def use_frost_stack(frost_effect: Stack) -> tuple[Stack, Stat]:
    if frost_effect.stack == 0:
        return frost_effect, Stat()

    new_frost_effect = frost_effect
    modifier = get_frost_modifier(new_frost_effect)
    new_frost_effect.decrease(1)

    return new_frost_effect, modifier


class FrostEffectState(TypedDict):
    frost_stack: Stack


class FrostEffect(Component):
    name: str = "프로스트 이펙트"
    critical_damage_per_stack: int
    maximum_stack: int

    def get_default_state(self) -> FrostEffectState:
        return {"frost_stack": Stack(maximum_stack=self.maximum_stack)}

    @reducer_method
    def increase_step(self, _: None, state: FrostEffectState):
        frost_stack = state["frost_stack"]
        frost_stack.increase(1)
        state["frost_stack"] = frost_stack

        return state, []

    @reducer_method
    def increase_three(self, _: None, state: FrostEffectState):
        frost_stack = state["frost_stack"]
        frost_stack.increase(3)
        state["frost_stack"] = frost_stack

        return state, []

    @view_method
    def buff(self, state: FrostEffectState):
        return Stat(
            critical_damage=self.critical_damage_per_stack * state["frost_stack"].stack
        )

    @view_method
    def running(self, state: FrostEffectState):
        return Running(
            id=self.id,
            name=self.name,
            lasting_duration=999_999_999,
            time_left=999_999_999,
            stack=state["frost_stack"].stack,
        )


def jupyter_thunder_shock_advantage(jupyter_thunder_shock: Periodic) -> Stat:
    if jupyter_thunder_shock.enabled():
        return Stat(final_damage_multiplier=12)

    return Stat()


class JupyterThunderState(TypedDict):
    frost_stack: Stack
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class JupyterThunderComponentProps(TypedDict):
    id: str
    name: str
    cooldown_duration: float
    delay: float
    periodic_initial_delay: Optional[float]
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float
    max_count: int


class JupyterThunder(Component):
    name: str
    cooldown_duration: float
    delay: float

    periodic_initial_delay: Optional[float] = None
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float

    max_count: int

    binds: dict[str, str] = {"frost_stack": ".프로스트 이펙트.frost_stack"}

    def get_default_state(self) -> JupyterThunderState:
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(
                interval=self.periodic_interval,
                initial_counter=self.periodic_initial_delay,
                time_left=0,
            ),
            "dynamics": Dynamics.model_validate({"stat": {}}),
            "frost_stack": Stack(maximum_stack=5),
        }

    def get_props(self) -> JupyterThunderComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
            "periodic_initial_delay": self.periodic_initial_delay,
            "periodic_interval": self.periodic_interval,
            "periodic_damage": self.periodic_damage,
            "periodic_hit": self.periodic_hit,
            "lasting_duration": self.lasting_duration,
            "max_count": self.max_count,
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        state: JupyterThunderState,
    ):
        cooldown, periodic, frost_stack = (
            state["cooldown"].model_copy(),
            state["periodic"].model_copy(),
            state["frost_stack"].model_copy(),
        )

        cooldown.elapse(time)
        dealing_events = []

        time_to_resolve = time
        periodic_state = periodic
        previous_count = periodic_state.count

        while time_to_resolve > 0:
            periodic_state, time_to_resolve = periodic_state.resolve_step(
                periodic_state, time_to_resolve
            )

            if periodic_state.count >= self.max_count:
                break

            if periodic_state.count == previous_count:
                continue

            if (periodic_state.count + 1) % 5 == 0:
                _, modifier = use_frost_stack(frost_stack)
            else:
                modifier = get_frost_modifier(frost_stack)

            dealing_events.append(
                EmptyEvent.dealt(
                    self.periodic_damage,
                    self.periodic_hit,
                    modifier=modifier,
                )
            )
            previous_count = periodic_state.count

        if periodic_state.count >= self.max_count:
            periodic_state.disable()

        state["periodic"] = periodic_state
        state["cooldown"] = cooldown
        state["frost_stack"] = frost_stack

        return state, [EmptyEvent.elapsed(time)] + dealing_events

    @reducer_method
    def use(self, _: None, state: JupyterThunderState):
        return periodic_trait.start_periodic_with_cooldown(
            state,
            {},
            **self.get_props(),
            damage=0,
            hit=0,
        )

    @view_method
    def validity(self, state: JupyterThunderState):
        return cooldown_trait.validity_view(state, **self.get_props())


class ThunderAttackSkillState(TypedDict):
    frost_stack: Stack
    jupyter_thunder_shock: Periodic
    cooldown: Cooldown
    dynamics: Dynamics


class ThunderAttackSkillComponentProps(TypedDict):
    id: str
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float


class ThunderAttackSkillComponent(
    Component,
):
    binds: dict[str, str] = {
        "frost_stack": ".프로스트 이펙트.frost_stack",
        "jupyter_thunder_shock": ".주피터 썬더.periodic",
    }
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    def get_default_state(self) -> ThunderAttackSkillState:
        return {
            "cooldown": Cooldown(time_left=0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
            "frost_stack": Stack(maximum_stack=5),
            "jupyter_thunder_shock": Periodic(
                interval=1, initial_counter=1, time_left=0
            ),
        }

    def get_props(self) -> ThunderAttackSkillComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "damage": self.damage,
            "hit": self.hit,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: ThunderAttackSkillState,
    ):
        if not state["cooldown"].available:
            return state, [EmptyEvent.rejected()]

        cooldown, frost_stack = (
            state["cooldown"].model_copy(),
            state["frost_stack"].model_copy(),
        )

        cooldown.set_time_left(
            state["dynamics"].stat.calculate_cooldown(self.cooldown_duration)
        )
        frost_stack, modifier = use_frost_stack(frost_stack)

        state["frost_stack"] = frost_stack
        state["cooldown"] = cooldown

        modifier += jupyter_thunder_shock_advantage(state["jupyter_thunder_shock"])

        return state, [
            EmptyEvent.dealt(self.damage, self.hit, modifier=modifier),
            EmptyEvent.delayed(self.delay),
        ]

    @reducer_method
    def elapse(self, time: float, state: ThunderAttackSkillState):
        return simple_attack.elapse(state, {"time": time})

    @view_method
    def validity(self, state: ThunderAttackSkillState):
        return cooldown_trait.validity_view(state, **self.get_props())


class CurrentField(Entity):
    field_periodics: list[Periodic] = []  # FIFO queue
    field_interval: float
    field_duration: float

    max_count: int

    last_force_triggered: float = 0.0
    force_trigger_interval: float

    stable_rng_counter: float = 0.0

    def stack_rng(self, rng_counter: float) -> bool:
        if self.last_force_triggered >= self.force_trigger_interval:
            self.last_force_triggered = 0
            self.create_new_current()
            return True

        self.stable_rng_counter += rng_counter

        if self.stable_rng_counter >= 1.0:
            self.stable_rng_counter -= 1.0
            self.create_new_current()
            return True

        return False

    def create_new_current(self):
        periodic = Periodic(
            interval=self.field_interval, initial_counter=self.field_interval
        )
        periodic.set_time_left(self.field_duration)

        self.field_periodics.append(periodic)
        self.field_periodics = self.field_periodics[-self.max_count :]

    def elapse(self, time: float) -> int:
        new_perdiodics = []
        tick_count = 0

        # current fields.
        for periodic in self.field_periodics:
            tick_count += periodic.elapse(time)

            if periodic.enabled():
                new_perdiodics.append(periodic)

        self.field_periodics = new_perdiodics
        self.last_force_triggered += time

        return tick_count


class ChainLightningVISkillState(TypedDict):
    frost_stack: Stack
    jupyter_thunder_shock: Periodic
    cooldown: Cooldown
    dynamics: Dynamics

    current_fields: CurrentField


class ChainLightningVIComponentProps(TypedDict):
    id: str
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    electric_current_prob: float
    electric_current_damage: float
    electric_current_hit: float

    electric_current_max_count: int
    electric_current_interval: float
    electric_current_duration: float
    electric_current_force_trigger_interval: float


class ChainLightningVIComponent(
    Component,
):
    binds: dict[str, str] = {
        "frost_stack": ".프로스트 이펙트.frost_stack",
        "jupyter_thunder_shock": ".주피터 썬더.periodic",
    }
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    electric_current_prob: float = 0.0
    electric_current_damage: float = 0.0
    electric_current_hit: float = 0.0

    electric_current_max_count: int
    electric_current_interval: float
    electric_current_duration: float
    electric_current_force_trigger_interval: float

    def get_default_state(self) -> ChainLightningVISkillState:
        return {
            "cooldown": Cooldown(time_left=0),
            "current_fields": CurrentField(
                max_count=self.electric_current_max_count,
                field_interval=self.electric_current_interval,
                field_duration=self.electric_current_duration,
                force_trigger_interval=self.electric_current_force_trigger_interval,
            ),
            "dynamics": Dynamics.model_validate({"stat": {}}),
            "frost_stack": Stack(maximum_stack=5),
            "jupyter_thunder_shock": Periodic(
                interval=1, initial_counter=1, time_left=0
            ),
        }

    def get_props(self) -> ChainLightningVIComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "damage": self.damage,
            "hit": self.hit,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
            "electric_current_prob": self.electric_current_prob,
            "electric_current_damage": self.electric_current_damage,
            "electric_current_hit": self.electric_current_hit,
            "electric_current_max_count": self.electric_current_max_count,
            "electric_current_interval": self.electric_current_interval,
            "electric_current_duration": self.electric_current_duration,
            "electric_current_force_trigger_interval": self.electric_current_force_trigger_interval,
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: ChainLightningVISkillState,
    ):
        if not state["cooldown"].available:
            return state, [EmptyEvent.rejected()]

        cooldown, frost_stack, current_fields = (
            state["cooldown"].model_copy(),
            state["frost_stack"].model_copy(),
            state["current_fields"].model_copy(deep=True),
        )

        cooldown.set_time_left(
            state["dynamics"].stat.calculate_cooldown(self.cooldown_duration)
        )

        frost_stack, modifier = use_frost_stack(frost_stack)
        modifier += jupyter_thunder_shock_advantage(state["jupyter_thunder_shock"])

        current_fields.stack_rng(self.electric_current_prob)

        state["frost_stack"] = frost_stack
        state["cooldown"] = cooldown
        state["current_fields"] = current_fields

        return state, [
            EmptyEvent.dealt(self.damage, self.hit, modifier=modifier),
            EmptyEvent.delayed(self.delay),
        ]

    @reducer_method
    def elapse(self, time: float, state: ChainLightningVISkillState):
        state, events = simple_attack.elapse(state, {"time": time})

        current_fields = state["current_fields"].model_copy(deep=True)
        electric_current_hits = current_fields.elapse(time)
        state["current_fields"] = current_fields

        events += [
            EmptyEvent.dealt(
                self.electric_current_damage,
                self.electric_current_hit,
            )
            for _ in range(electric_current_hits)
        ]

        return state, events

    @view_method
    def validity(self, state: ChainLightningVISkillState):
        return cooldown_trait.validity_view(state, **self.get_props())

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit


class ThunderBreakState(TypedDict):
    frost_stack: Stack
    jupyter_thunder_shock: Periodic
    cooldown: Cooldown
    dynamics: Dynamics
    periodic: Periodic


class ThunderBreakComponentProps(TypedDict):
    id: str
    name: str
    cooldown_duration: float
    delay: float
    periodic_initial_delay: Optional[float]
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float
    decay_rate: float
    max_count: int


class ThunderBreak(Component):
    name: str
    cooldown_duration: float
    delay: float

    periodic_initial_delay: Optional[float] = None
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float

    decay_rate: float
    max_count: int

    binds: dict[str, str] = {
        "frost_stack": ".프로스트 이펙트.frost_stack",
        "jupyter_thunder_shock": ".주피터 썬더.periodic",
    }

    def get_default_state(self) -> ThunderBreakState:
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(
                interval=self.periodic_interval,
                initial_counter=self.periodic_initial_delay,
                time_left=0,
            ),
            "dynamics": Dynamics.model_validate({"stat": {}}),
            "frost_stack": Stack(maximum_stack=5),
            "jupyter_thunder_shock": Periodic(
                interval=1, initial_counter=1, time_left=0
            ),
        }

    def get_props(self) -> ThunderBreakComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
            "periodic_initial_delay": self.periodic_initial_delay,
            "periodic_interval": self.periodic_interval,
            "periodic_damage": self.periodic_damage,
            "periodic_hit": self.periodic_hit,
            "lasting_duration": self.lasting_duration,
            "decay_rate": self.decay_rate,
            "max_count": self.max_count,
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        state: ThunderBreakState,
    ):
        cooldown, periodic, frost_stack = (
            state["cooldown"].model_copy(),
            state["periodic"].model_copy(),
            state["frost_stack"].model_copy(),
        )

        cooldown.elapse(time)
        dealing_events = []

        time_to_resolve = time
        previous_count = periodic.count

        while time_to_resolve > 0:
            periodic, time_to_resolve = periodic.resolve_step(periodic, time_to_resolve)

            if periodic.count > self.max_count:
                break

            if previous_count == periodic.count:
                continue

            frost_stack, modifier = use_frost_stack(frost_stack)

            modifier += jupyter_thunder_shock_advantage(state["jupyter_thunder_shock"])

            dealing_events.append(
                EmptyEvent.dealt(
                    self.periodic_damage * self._get_decay_factor(periodic),
                    self.periodic_hit,
                    modifier=modifier,
                )
            )
            previous_count = periodic.count

        if periodic.count >= self.max_count:
            periodic.disable()

        state["periodic"] = periodic
        state["cooldown"] = cooldown
        state["frost_stack"] = frost_stack

        return state, [EmptyEvent.elapsed(time)] + dealing_events

    def _get_decay_factor(self, periodic: Periodic):
        return self.decay_rate**periodic.count

    @reducer_method
    def use(self, _: None, state: ThunderBreakState):
        return periodic_trait.start_periodic_with_cooldown(
            state,
            {},
            **self.get_props(),
            damage=0,
            hit=0,
        )

    @view_method
    def validity(self, state: ThunderBreakState):
        return cooldown_trait.validity_view(state, **self.get_props())
