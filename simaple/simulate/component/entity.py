from typing import Optional

from simaple.simulate.base import Entity


class DurationState(Entity):
    time_left: float
    assigned_duration: float = 0.0

    def enabled(self):
        return self.time_left > 0

    def elapse(self, time: float):
        self.time_left -= time

    def set_time_left(self, time: float):
        self.time_left = time
        self.assigned_duration = time

    def get_elapsed_time(self) -> float:
        return self.assigned_duration - self.time_left


class CooldownState(Entity):
    time_left: float

    @property
    def available(self):
        return self.time_left <= 0

    def elapse(self, time: float):
        self.time_left -= time

    def set_time_left(self, time: float):
        self.time_left = time


class IntervalState(Entity):
    interval_counter: float = 0.0
    interval: float
    interval_time_left: float = 0.0
    count: int = 0

    def set_time_left(self, time: float, initial_counter: Optional[float] = None):
        self.interval_time_left = time
        self.interval_counter = (
            initial_counter if initial_counter is not None else self.interval
        )
        self.count = 0

    def enabled(self):
        return self.interval_time_left > 0

    def elapse(self, time: float) -> int:
        maximum_elapsed = max(0, int(self.interval_time_left // self.interval))
        self.interval_time_left -= time
        self.interval_counter -= time

        if self.interval_counter < 0:
            lapse_count = int(self.interval_counter // self.interval)
            self.interval_counter = self.interval_counter % self.interval
            count = min(maximum_elapsed, lapse_count * -1)
            self.count += count
            return count

        return 0

    def resolving(self, time: float):
        maximum_elapsed = max(0, int(self.interval_time_left // self.interval))

        self.interval_time_left -= time
        self.interval_counter -= time
        elapse_count = 0

        while self.interval_counter <= 0 and elapse_count < maximum_elapsed:
            self.interval_counter += self.interval
            elapse_count += 1
            yield 1
            self.count += 1

    def disable(self):
        self.interval_time_left = 0


class StackState(Entity):
    stack: int = 0
    maximum_stack: int

    def reset(self, value: int = 0):
        self.stack = value

    def increase(self, value: int = 1):
        self.stack = min(self.maximum_stack, self.stack + value)

    def get_stack(self) -> int:
        return self.stack

    def decrease(self, value: int = 1):
        self.stack -= value
