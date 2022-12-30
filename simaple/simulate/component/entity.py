from typing import Optional

from simaple.simulate.base import Entity


class Lasting(Entity):
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


class Cooldown(Entity):
    time_left: float

    @property
    def available(self):
        return self.time_left <= 0

    def elapse(self, time: float):
        self.time_left -= time

    def set_time_left(self, time: float):
        self.time_left = time


class Cycle(Entity):
    tick: int
    period: int

    def step(self):
        self.tick += 1
        self.tick = self.tick % self.period

    def get_tick(self) -> int:
        return self.tick

    def clear(self):
        self.tick = 0


class Periodic(Entity):
    interval_counter: float = 0.0
    interval: float
    time_left: float = 0.0
    count: int = 0

    def set_time_left(self, time: float, initial_counter: Optional[float] = None):
        self.time_left = time
        self.interval_counter = (
            initial_counter if initial_counter is not None else self.interval
        )
        self.count = 0

    def enabled(self):
        return self.time_left > 0

    def elapse(self, time: float) -> int:
        maximum_elapsed = max(0, int(self.time_left // self.interval))
        self.time_left -= time
        self.interval_counter -= time

        if self.interval_counter < 0:
            lapse_count = int(self.interval_counter // self.interval)
            self.interval_counter = self.interval_counter % self.interval
            count = min(maximum_elapsed, lapse_count * -1)
            self.count += count
            return count

        return 0

    def resolving(self, time: float):
        maximum_elapsed = max(0, int(self.time_left // self.interval))

        self.time_left -= time
        self.interval_counter -= time
        elapse_count = 0

        while self.interval_counter <= 0 and elapse_count < maximum_elapsed:
            self.interval_counter += self.interval
            elapse_count += 1
            yield 1
            self.count += 1

    def disable(self):
        self.time_left = 0


class Stack(Entity):
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


class Keydown(Entity):
    interval: float
    interval_counter: float = 0.0
    time_left: float = 0

    @property
    def running(self) -> bool:
        return self.time_left > 0

    def get_next_delay(self) -> float:
        return min(self.interval_counter, self.time_left)

    def start(self, maximum_keydown_time: float, prepare_delay: float):
        self.interval_counter = prepare_delay
        self.time_left = maximum_keydown_time

    def stop(self):
        self.time_left = 0

    def resolving(self, time: float):
        resolving_time_left = self.time_left - max(0, self.interval_counter)
        self.time_left -= time
        self.interval_counter -= time

        # pylint:disable=chained-comparison
        while resolving_time_left >= 0 and self.interval_counter <= 0:
            yield 1
            self.interval_counter += self.interval
            resolving_time_left -= self.interval
