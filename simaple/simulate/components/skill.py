from simaple.simulate.base import Component, State, dispatcher_method
from simaple.simulate.event import damage_event


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
            lapse_count = self.time_left // self.interval
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
        return cooldown_state, None

    @dispatcher_method
    def use(self, _: None, cooldown_state: CooldownState):
        cooldown_state = cooldown_state.copy()

        if not cooldown_state.available:
            return cooldown_state, None

        cooldown_state.set_time_left(self.cooldown)

        return cooldown_state, damage_event(
            self.name, self.damage, self.hit, self.delay
        )
