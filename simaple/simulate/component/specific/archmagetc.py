from simaple.core.base import Stat
from simaple.simulate.component.base import (
    Component,
    ReducerState,
    reducer_method,
    view_method,
)
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.state_fragment import (
    CooldownState,
    IntervalState,
    StackState,
)
from simaple.simulate.component.trait.impl import (
    CooldownValidityTrait,
    StartIntervalWithoutDamageTrait,
    UseSimpleAttackTrait,
)
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


def get_frost_modifier(frost_effect: StackState) -> Stat:
    return Stat(damage_multiplier=frost_effect.stack * 12)  # Magic Number


def use_frost_stack(frost_effect: StackState) -> tuple[StackState, Stat]:
    if frost_effect.stack == 0:
        return frost_effect, Stat()

    new_frost_effect = frost_effect
    modifier = get_frost_modifier(new_frost_effect)
    new_frost_effect.decrease(1)

    return new_frost_effect, modifier


class FrostEffectState(ReducerState):
    frost_stack: StackState


class FrostEffect(Component):
    name: str = "프로스트 이펙트"
    critical_damage_per_stack: int
    maximum_stack: int

    def get_default_state(self):
        return {"frost_stack": StackState(maximum_stack=self.maximum_stack)}

    @reducer_method
    def increase_step(self, _: None, state: FrostEffectState):
        state = state.copy()
        state.frost_stack.increase(1)
        return state, []

    @reducer_method
    def increase_three(self, _: None, state: FrostEffectState):
        state = state.copy()
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
            duration=999_999_999,
            time_left=999_999_999,
            stack=state.frost_stack.stack,
        )


def jupyter_thunder_shock_advantage(jupyter_thunder_shock: IntervalState) -> Stat:
    if jupyter_thunder_shock.enabled():
        return Stat(final_damage_multiplier=12)

    return Stat()


class JupyterThunderState(ReducerState):
    frost_stack: StackState
    cooldown_state: CooldownState
    interval_state: IntervalState
    dynamics: Dynamics


class JupyterThunder(
    SkillComponent, StartIntervalWithoutDamageTrait, CooldownValidityTrait
):
    name: str
    cooldown: float = 0.0
    delay: float

    tick_interval: float
    tick_damage: float
    tick_hit: float
    duration: float = 10_000  # very long enough

    max_count: int

    binds: dict[str, str] = {"frost_stack": ".프로스트 이펙트.frost_stack"}

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
            "interval_state": IntervalState(interval=self.tick_interval, time_left=0),
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        state: JupyterThunderState,
    ):
        state = state.copy()

        state.cooldown_state.elapse(time)
        dealing_events = []

        for _ in state.interval_state.resolving(time):
            if state.interval_state.count >= self.max_count:
                break

            if (state.interval_state.count + 1) % 5 == 0:
                _, modifier = use_frost_stack(state.frost_stack)
            else:
                modifier = get_frost_modifier(state.frost_stack)

            dealing_events.append(
                self.event_provider.dealt(
                    self.tick_damage,
                    self.tick_hit,
                    modifier=modifier,
                )
            )

        if state.interval_state.count >= self.max_count:
            state.interval_state.disable()

        return state, [self.event_provider.elapsed(time)] + dealing_events

    @reducer_method
    def use(self, _: None, state: JupyterThunderState):
        return self.use_tick_emitting_without_damage_trait(state)

    @view_method
    def validity(self, state: JupyterThunderState):
        return self.validity_in_cooldown_trait(state)

    def _get_duration(self) -> float:
        return self.duration


class ThunderAttackSkillState(ReducerState):
    frost_stack: StackState
    jupyter_thunder_shock: IntervalState
    cooldown_state: CooldownState
    dynamics: Dynamics


class ThunderAttackSkillComponent(
    SkillComponent, UseSimpleAttackTrait, CooldownValidityTrait
):
    binds: dict[str, str] = {
        "frost_stack": ".프로스트 이펙트.frost_stack",
        "jupyter_thunder_shock": ".주피터 썬더.interval_state",
    }
    name: str
    damage: float
    hit: float
    cooldown: float
    delay: float

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: ThunderAttackSkillState,
    ):
        state = state.copy()

        if not state.cooldown_state.available:
            return state, self.event_provider.rejected()

        state.cooldown_state.set_time_left(
            state.dynamics.stat.calculate_cooldown(self.cooldown)
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
    frost_stack: StackState
    jupyter_thunder_shock: IntervalState
    cooldown_state: CooldownState
    dynamics: Dynamics
    interval_state: IntervalState


class ThunderBreak(
    SkillComponent, StartIntervalWithoutDamageTrait, CooldownValidityTrait
):
    name: str
    cooldown: float = 0.0
    delay: float

    tick_interval: float
    tick_damage: float
    tick_hit: float
    duration: float = 10_000  # very long enough

    decay_rate: float
    max_count: int

    binds: dict[str, str] = {
        "frost_stack": ".프로스트 이펙트.frost_stack",
        "jupyter_thunder_shock": ".주피터 썬더.interval_state",
    }

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
            "interval_state": IntervalState(interval=self.tick_interval, time_left=0),
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        state: ThunderBreakState,
    ):
        state = state.copy()

        state.cooldown_state.elapse(time)
        dealing_events = []

        for _ in state.interval_state.resolving(time):
            if state.interval_state.count >= self.max_count:
                break

            frost_stack, modifier = use_frost_stack(state.frost_stack)
            state.frost_stack = frost_stack

            modifier += jupyter_thunder_shock_advantage(state.jupyter_thunder_shock)

            dealing_events.append(
                self.event_provider.dealt(
                    self.tick_damage * self._get_decay_factor(state),
                    self.tick_hit,
                    modifier=modifier,
                )
            )

        if state.interval_state.count >= self.max_count:
            state.interval_state.disable()

        return state, [self.event_provider.elapsed(time)] + dealing_events

    def _get_decay_factor(self, state: ThunderBreakState):
        return self.decay_rate**state.interval_state.count

    @reducer_method
    def use(self, _: None, state: ThunderBreakState):
        return self.use_tick_emitting_without_damage_trait(state)

    @view_method
    def validity(self, state: ThunderBreakState):
        return self.validity_in_cooldown_trait(state)

    def _get_duration(self) -> float:
        return self.duration
