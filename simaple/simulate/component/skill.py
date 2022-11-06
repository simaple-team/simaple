from simaple.core.base import Stat
from simaple.simulate.base import State
from simaple.simulate.component.base import Component, reducer_method


class DurationState(State):
    time_left: float

    def enabled(self):
        return self.time_left > 0

    def elapse(self, time: float):
        self.time_left -= time

    def set_time_left(self, time: float):
        self.time_left = time


class CooldownState(State):
    time_left: float

    @property
    def available(self):
        return self.time_left <= 0

    def elapse(self, time: float):
        self.time_left -= time

    def set_time_left(self, time: float):
        self.time_left = time


class IntervalState(State):
    interval_counter: float = 0.0
    interval: float
    interval_time_left: float = 0.0

    def set_time_left(self, time: float):
        self.interval_time_left = time
        self.interval_counter = self.interval

    def enabled(self):
        return self.interval_time_left > 0

    def elapse(self, time: float) -> int:
        maximum_elapsed = max(0, int(self.interval_time_left // self.interval))
        self.interval_time_left -= time
        self.interval_counter -= time

        if self.interval_counter < 0:
            lapse_count = int(self.interval_counter // self.interval)
            self.interval_counter = self.interval_counter % self.interval
            return min(maximum_elapsed, lapse_count * -1)

        return 0


class AttackSkillComponent(Component):
    name: str
    damage: float
    hit: float
    cooldown: float = 0.0
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
    def use(self, _: None, cooldown_state: CooldownState):
        cooldown_state = cooldown_state.copy()

        if not cooldown_state.available:
            return cooldown_state, self.event_provider.rejected()

        cooldown_state.set_time_left(self.cooldown)

        return cooldown_state, [
            self.event_provider.dealt(self.damage, self.hit),
            self.event_provider.delayed(self.delay),
        ]

    @reducer_method
    def reset_cooldown(self, _: None, cooldown_state: CooldownState):
        cooldown_state = cooldown_state.copy()
        cooldown_state.set_time_left(0)
        return cooldown_state, None


class BuffSkillComponent(Component):
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
        self, _: None, cooldown_state: CooldownState, duration_state: DurationState
    ):
        cooldown_state = cooldown_state.copy()
        duration_state = duration_state.copy()

        if not cooldown_state.available:
            return cooldown_state, self.event_provider.rejected()

        cooldown_state.set_time_left(self.cooldown)
        duration_state.set_time_left(self.duration)

        return (cooldown_state, duration_state), self.event_provider.delayed(self.delay)

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


class TickDamageConfiguratedAttackSkillComponent(Component):
    name: str
    damage: float
    hit: float
    cooldown: float = 0.0
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
        self, _: None, cooldown_state: CooldownState, interval_state: IntervalState
    ):
        cooldown_state = cooldown_state.copy()
        interval_state = interval_state.copy()

        if not cooldown_state.available:
            return (cooldown_state, interval_state), self.event_provider.rejected()

        cooldown_state.set_time_left(self.cooldown)
        interval_state.set_time_left(self.duration)

        return (cooldown_state, interval_state), [
            self.event_provider.dealt(self.damage, self.hit),
            self.event_provider.delayed(self.delay),
        ]
