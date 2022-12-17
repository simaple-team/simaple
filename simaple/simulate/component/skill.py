from typing import Optional

from simaple.core.base import Stat
from simaple.simulate.component.base import Component, reducer_method, view_method
from simaple.simulate.component.state import CooldownState, DurationState, IntervalState
from simaple.simulate.component.view import Running, Validity
from simaple.simulate.event import EventProvider, NamedEventProvider
from simaple.simulate.global_property import Dynamics


class SkillComponent(Component):
    disable_validity: bool = False
    modifier: Optional[Stat]
    cooldown: float
    delay: float

    @property
    def event_provider(self) -> EventProvider:
        return NamedEventProvider(self.name, self.modifier)

    def invalidate_if_disabled(self, validity: Validity):
        if self.disable_validity:
            validity = validity.copy()
            validity.valid = False
            return validity

        return validity


class AttackSkillComponent(SkillComponent):
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
    def elapse(self, time: float, cooldown_state: CooldownState):
        cooldown_state = cooldown_state.copy()
        cooldown_state.elapse(time)
        return cooldown_state, self.event_provider.elapsed(time)

    @reducer_method
    def use(self, _: None, cooldown_state: CooldownState, dynamics: Dynamics):
        cooldown_state = cooldown_state.copy()

        if not cooldown_state.available:
            return (cooldown_state, dynamics), self.event_provider.rejected()

        cooldown_state.set_time_left(dynamics.stat.calculate_cooldown(self.cooldown))

        return (cooldown_state, dynamics), [
            self.event_provider.dealt(self.damage, self.hit),
            self.event_provider.delayed(self.delay),
        ]

    @reducer_method
    def reset_cooldown(self, _: None, cooldown_state: CooldownState):
        cooldown_state = cooldown_state.copy()
        cooldown_state.set_time_left(0)
        return cooldown_state, None

    @view_method
    def validity(self, cooldown_state):
        return self.invalidate_if_disabled(
            Validity(
                name=self.name,
                time_left=max(0, cooldown_state.time_left),
                valid=cooldown_state.available,
                cooldown=self.cooldown,
            )
        )


class MultipleAttackSkillComponent(AttackSkillComponent):
    multiple: int

    @reducer_method
    def use(self, _: None, cooldown_state: CooldownState, dynamics: Dynamics):
        cooldown_state = cooldown_state.copy()

        if not cooldown_state.available:
            return (cooldown_state, dynamics), self.event_provider.rejected()

        cooldown_state.set_time_left(dynamics.stat.calculate_cooldown(self.cooldown))

        return (cooldown_state, dynamics), [
            self.event_provider.dealt(self.damage, self.hit)
            for _ in range(self.multiple)
        ] + [self.event_provider.delayed(self.delay)]


class BuffSkillComponent(SkillComponent):
    stat: Stat
    cooldown: float = 0.0
    delay: float
    duration: float
    # TODO: use rem, red argument to apply cooltime reduction and buff remnance

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
            "duration_state": DurationState(time_left=0),
        }

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        duration_state: DurationState,
        dynamics: Dynamics,
    ):
        cooldown_state = cooldown_state.copy()
        duration_state = duration_state.copy()

        if not cooldown_state.available:
            return (
                cooldown_state,
                duration_state,
                dynamics,
            ), self.event_provider.rejected()

        cooldown_state.set_time_left(dynamics.stat.calculate_cooldown(self.cooldown))

        duration_state.set_time_left(
            dynamics.stat.calculate_buff_duration(self.duration)
        )

        return (cooldown_state, duration_state, dynamics), self.event_provider.delayed(
            self.delay
        )

    @reducer_method
    def elapse(
        self, time: float, cooldown_state: CooldownState, duration_state: DurationState
    ):
        cooldown_state = cooldown_state.copy()
        duration_state = duration_state.copy()

        cooldown_state.elapse(time)
        duration_state.elapse(time)

        return (cooldown_state, duration_state), [
            self.event_provider.elapsed(time),
        ]

    @view_method
    def validity(self, cooldown_state: CooldownState):
        return self.invalidate_if_disabled(
            Validity(
                name=self.name,
                time_left=max(0, cooldown_state.time_left),
                valid=cooldown_state.available,
                cooldown=self.cooldown,
            )
        )

    @view_method
    def buff(self, duration_state: DurationState) -> Optional[Stat]:
        if duration_state.enabled():
            return self.stat

        return None

    @view_method
    def running(self, duration_state: DurationState) -> Running:
        return Running(name=self.name, time_left=duration_state.time_left)


class TickDamageConfiguratedAttackSkillComponent(SkillComponent):
    name: str
    damage: float
    hit: float
    cooldown: float
    delay: float

    tick_interval: float
    tick_damage: float
    tick_hit: float
    duration: float

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
            "interval_state": IntervalState(interval=self.tick_interval, time_left=0),
        }

    @reducer_method
    def elapse(
        self, time: float, cooldown_state: CooldownState, interval_state: IntervalState
    ):
        cooldown_state = cooldown_state.copy()
        interval_state = interval_state.copy()

        cooldown_state.elapse(time)
        lapse_count = interval_state.elapse(time)

        return (cooldown_state, interval_state), [self.event_provider.elapsed(time)] + [
            self.event_provider.dealt(self.tick_damage, self.tick_hit)
            for _ in range(lapse_count)
        ]

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
            return (
                cooldown_state,
                interval_state,
                dynamics,
            ), self.event_provider.rejected()

        cooldown_state.set_time_left(dynamics.stat.calculate_cooldown(self.cooldown))
        interval_state.set_time_left(self.duration)

        return (cooldown_state, interval_state, dynamics), [
            self.event_provider.dealt(self.damage, self.hit),
            self.event_provider.delayed(self.delay),
        ]

    @view_method
    def validity(self, cooldown_state):
        return self.invalidate_if_disabled(
            Validity(
                name=self.name,
                time_left=max(0, cooldown_state.time_left),
                valid=cooldown_state.available,
                cooldown=self.cooldown,
            )
        )

    @view_method
    def running(self, interval_state: IntervalState) -> Running:
        return Running(name=self.name, time_left=interval_state.interval_time_left)


class DOTSkillComponent(Component):
    name: str

    tick_interval: float = 1_000
    tick_damage: float
    tick_hit: int = 1
    duration: float

    def get_default_state(self):
        return {
            "interval_state": IntervalState(interval=self.tick_interval, time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, interval_state: IntervalState):
        interval_state = interval_state.copy()

        lapse_count = interval_state.elapse(time)

        return interval_state, [
            self.event_provider.dealt(self.tick_damage, self.tick_hit)
            for _ in range(lapse_count)
        ]

    @reducer_method
    def apply(self, _: None, interval_state: IntervalState):
        interval_state = interval_state.copy()

        interval_state.set_time_left(self.duration)

        return interval_state, None
