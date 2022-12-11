from simaple.core.base import Stat
from simaple.simulate.component.base import Component, reducer_method, view_method
from simaple.simulate.component.skill import (
    AttackSkillComponent,
    CooldownState,
    IntervalState,
    StackState,
)
from simaple.simulate.component.view import Validity
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


class FrostEffect(Component):
    name: str = "프로스트 이펙트"
    critical_damage_per_stack: int
    maximum_stack: int

    def get_default_state(self):
        return {"frost_stack": StackState(maximum_stack=self.maximum_stack)}

    @reducer_method
    def increase_step(self, _: None, frost_stack: StackState):
        frost_stack = frost_stack.copy()
        frost_stack.increase(1)
        return frost_stack, []

    @reducer_method
    def increase_three(self, _: None, frost_stack: StackState):
        frost_stack = frost_stack.copy()
        frost_stack.increase(3)
        return frost_stack, []

    @view_method
    def buff(self, frost_stack: StackState):
        return Stat(critical_damage=self.critical_damage_per_stack * frost_stack.stack)

    @view_method
    def stack(self, frost_stack: StackState):
        return frost_stack.get_stack()


def jupyter_thunder_shock_advantage(jupyter_thunder_shock: IntervalState) -> Stat:
    if jupyter_thunder_shock.enabled():
        return Stat(final_damage_multiplier=12)

    return Stat()


class JupyterThunder(Component):
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
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        frost_stack: StackState,
    ):
        cooldown_state = cooldown_state.copy()
        interval_state = interval_state.copy()

        cooldown_state.elapse(time)
        dealing_events = []

        for _ in interval_state.resolving(time):
            if interval_state.count >= self.max_count:
                break

            if (interval_state.count + 1) % 5 == 0:
                frost_stack, modifier = use_frost_stack(frost_stack)
            else:
                modifier = get_frost_modifier(frost_stack)

            dealing_events.append(
                self.event_provider.dealt(
                    self.tick_damage,
                    self.tick_hit,
                    modifier=modifier,
                )
            )

        if interval_state.count >= self.max_count:
            interval_state.disable()

        return (cooldown_state, interval_state, frost_stack), [
            self.event_provider.elapsed(time)
        ] + dealing_events

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        dynamics: Dynamics,
    ):
        cooldown_state = cooldown_state.copy()
        interval_state = interval_state.copy()

        if not cooldown_state.available:
            return (cooldown_state, interval_state), self.event_provider.rejected()

        cooldown_state.set_time_left(dynamics.stat.calculate_cooldown(self.cooldown))
        interval_state.set_time_left(self.duration)

        return (cooldown_state, interval_state, dynamics), [
            self.event_provider.delayed(self.delay),
        ]

    @view_method
    def validity(self, cooldown_state):
        return Validity(
            name=self.name,
            time_left=max(0, cooldown_state.time_left),
            valid=cooldown_state.available,
            cooldown=self.cooldown,
        )


class ThunderAttackSkillComponent(AttackSkillComponent):
    binds: dict[str, str] = {
        "frost_stack": ".프로스트 이펙트.frost_stack",
        "jupyter_thunder_shock": ".주피터 썬더.interval_state",
    }

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        frost_stack: StackState,
        jupyter_thunder_shock: IntervalState,
        dynamics: Dynamics,
    ):
        cooldown_state = cooldown_state.copy()

        if not cooldown_state.available:
            return (
                cooldown_state,
                frost_stack,
                jupyter_thunder_shock,
                dynamics,
            ), self.event_provider.rejected()

        cooldown_state.set_time_left(dynamics.stat.calculate_cooldown(self.cooldown))

        frost_stack, modifier = use_frost_stack(frost_stack)
        modifier += jupyter_thunder_shock_advantage(jupyter_thunder_shock)

        return (cooldown_state, frost_stack, jupyter_thunder_shock, dynamics), [
            self.event_provider.dealt(self.damage, self.hit, modifier=modifier),
            self.event_provider.delayed(self.delay),
        ]


class ThunderBreak(Component):
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
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        jupyter_thunder_shock: IntervalState,
        frost_stack: StackState,
    ):
        cooldown_state = cooldown_state.copy()
        interval_state = interval_state.copy()

        cooldown_state.elapse(time)
        dealing_events = []

        for _ in interval_state.resolving(time):
            if interval_state.count >= self.max_count:
                break

            frost_stack, modifier = use_frost_stack(frost_stack)
            modifier += jupyter_thunder_shock_advantage(jupyter_thunder_shock)

            dealing_events.append(
                self.event_provider.dealt(
                    self.tick_damage * self._get_decay_factor(interval_state),
                    self.tick_hit,
                    modifier=modifier,
                )
            )

        if interval_state.count >= self.max_count:
            interval_state.disable()

        return (cooldown_state, interval_state, jupyter_thunder_shock, frost_stack), [
            self.event_provider.elapsed(time)
        ] + dealing_events

    def _get_decay_factor(self, interval_state):
        return self.decay_rate**interval_state.count

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        dynamics: Dynamics,
    ):
        cooldown_state = cooldown_state.copy()
        interval_state = interval_state.copy()

        if not cooldown_state.available:
            return (cooldown_state, interval_state), self.event_provider.rejected()

        cooldown_state.set_time_left(dynamics.stat.calculate_cooldown(self.cooldown))
        interval_state.set_time_left(self.duration)

        return (cooldown_state, interval_state, dynamics), [
            self.event_provider.delayed(self.delay),
        ]

    @view_method
    def validity(self, cooldown_state):
        return Validity(
            name=self.name,
            time_left=max(0, cooldown_state.time_left),
            valid=cooldown_state.available,
            cooldown=self.cooldown,
        )
