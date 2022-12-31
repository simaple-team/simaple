from simaple.core.base import Stat
from simaple.simulate.component.base import (
    Component,
    ReducerState,
    reducer_method,
    view_method,
)
from simaple.simulate.component.entity import Cooldown, Periodic, Stack
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import (
    CooldownValidityTrait,
    UsePeriodicDamageTrait,
    UseSimpleAttackTrait,
)
from simaple.simulate.component.view import Running
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


class FrostEffectState(ReducerState):
    frost_stack: Stack


class FrostEffect(Component):
    name: str = "프로스트 이펙트"
    critical_damage_per_stack: int
    maximum_stack: int

    def get_default_state(self):
        return {"frost_stack": Stack(maximum_stack=self.maximum_stack)}

    @reducer_method
    def increase_step(self, _: None, state: FrostEffectState):
        state = state.deepcopy()
        state.frost_stack.increase(1)
        return state, []

    @reducer_method
    def increase_three(self, _: None, state: FrostEffectState):
        state = state.deepcopy()
        state.frost_stack.increase(3)
        return state, []

    @view_method
    def buff(self, state: FrostEffectState):
        return Stat(
            critical_damage=self.critical_damage_per_stack * state.frost_stack.stack
        )

    @view_method
    def running(self, state: FrostEffectState):
        return Running(
            name=self.name,
            lasting_duration=999_999_999,
            time_left=999_999_999,
            stack=state.frost_stack.stack,
        )


def jupyter_thunder_shock_advantage(jupyter_thunder_shock: Periodic) -> Stat:
    if jupyter_thunder_shock.enabled():
        return Stat(final_damage_multiplier=12)

    return Stat()


class JupyterThunderState(ReducerState):
    frost_stack: Stack
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class JupyterThunder(SkillComponent, UsePeriodicDamageTrait, CooldownValidityTrait):
    name: str
    cooldown_duration: float
    delay: float

    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float

    max_count: int

    binds: dict[str, str] = {"frost_stack": ".프로스트 이펙트.frost_stack"}

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(interval=self.periodic_interval, time_left=0),
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        state: JupyterThunderState,
    ):
        state = state.deepcopy()

        state.cooldown.elapse(time)
        dealing_events = []

        for _ in state.periodic.resolving(time):
            if state.periodic.count >= self.max_count:
                break

            if (state.periodic.count + 1) % 5 == 0:
                _, modifier = use_frost_stack(state.frost_stack)
            else:
                modifier = get_frost_modifier(state.frost_stack)

            dealing_events.append(
                self.event_provider.dealt(
                    self.periodic_damage,
                    self.periodic_hit,
                    modifier=modifier,
                )
            )

        if state.periodic.count >= self.max_count:
            state.periodic.disable()

        return state, [self.event_provider.elapsed(time)] + dealing_events

    @reducer_method
    def use(self, _: None, state: JupyterThunderState):
        return self.use_periodic_damage_trait(state)

    @view_method
    def validity(self, state: JupyterThunderState):
        return self.validity_in_cooldown_trait(state)

    def _get_lasting_duration(self, state: JupyterThunderState) -> float:
        return self.lasting_duration


class ThunderAttackSkillState(ReducerState):
    frost_stack: Stack
    jupyter_thunder_shock: Periodic
    cooldown: Cooldown
    dynamics: Dynamics


class ThunderAttackSkillComponent(
    SkillComponent, UseSimpleAttackTrait, CooldownValidityTrait
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

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: ThunderAttackSkillState,
    ):
        state = state.deepcopy()

        if not state.cooldown.available:
            return state, [self.event_provider.rejected()]

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self.cooldown_duration)
        )

        frost_stack, modifier = use_frost_stack(state.frost_stack)
        state.frost_stack = frost_stack
        modifier += jupyter_thunder_shock_advantage(state.jupyter_thunder_shock)

        return state, [
            self.event_provider.dealt(self.damage, self.hit, modifier=modifier),
            self.event_provider.delayed(self.delay),
        ]

    @reducer_method
    def elapse(self, time: float, state: ThunderAttackSkillState):
        return self.elapse_simple_attack(time, state)

    @view_method
    def validity(self, state: ThunderAttackSkillState):
        return self.validity_in_cooldown_trait(state)

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit


class ThunderBreakState(ReducerState):
    frost_stack: Stack
    jupyter_thunder_shock: Periodic
    cooldown: Cooldown
    dynamics: Dynamics
    periodic: Periodic


class ThunderBreak(SkillComponent, UsePeriodicDamageTrait, CooldownValidityTrait):
    name: str
    cooldown_duration: float
    delay: float

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

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(interval=self.periodic_interval, time_left=0),
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        state: ThunderBreakState,
    ):
        state = state.deepcopy()

        state.cooldown.elapse(time)
        dealing_events = []

        for _ in state.periodic.resolving(time):
            if state.periodic.count >= self.max_count:
                break

            frost_stack, modifier = use_frost_stack(state.frost_stack)
            state.frost_stack = frost_stack

            modifier += jupyter_thunder_shock_advantage(state.jupyter_thunder_shock)

            dealing_events.append(
                self.event_provider.dealt(
                    self.periodic_damage * self._get_decay_factor(state),
                    self.periodic_hit,
                    modifier=modifier,
                )
            )

        if state.periodic.count >= self.max_count:
            state.periodic.disable()

        return state, [self.event_provider.elapsed(time)] + dealing_events

    def _get_decay_factor(self, state: ThunderBreakState):
        return self.decay_rate**state.periodic.count

    @reducer_method
    def use(self, _: None, state: ThunderBreakState):
        return self.use_periodic_damage_trait(state)

    @view_method
    def validity(self, state: ThunderBreakState):
        return self.validity_in_cooldown_trait(state)

    def _get_lasting_duration(self, state: ThunderBreakState) -> float:
        return self.lasting_duration
