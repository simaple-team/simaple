from simaple.core.base import Stat
from simaple.simulate.base import State
from simaple.simulate.component.base import Component, dispatcher_method


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
    time_left: float
    interval: int

    def elapse(self, time: float) -> int:
        self.time_left -= time
        if self.time_left < 0:
            lapse_count = int(self.time_left // self.interval)
            self.time_left = self.time_left % self.interval
            return lapse_count

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

    @dispatcher_method
    def elapse(self, time: float, cooldown_state: CooldownState):
        cooldown_state = cooldown_state.copy()
        cooldown_state.elapse(time)
        return cooldown_state, self.event_provider.elapsed(time)

    @dispatcher_method
    def use(self, _: None, cooldown_state: CooldownState):
        cooldown_state = cooldown_state.copy()

        if not cooldown_state.available:
            return cooldown_state, self.event_provider.rejected()

        cooldown_state.set_time_left(self.cooldown)

        return cooldown_state, [
            self.event_provider.dealt(self.damage, self.hit),
            self.event_provider.delayed(self.delay),
        ]


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

    @dispatcher_method
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

    @dispatcher_method
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
