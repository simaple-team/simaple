from typing import Optional

from simaple.simulate.base import Entity


class Lasting(Entity):
    time_left: float
    assigned_duration: float = 0.0

    def enabled(self):
        return self.time_left > 0

    def get_elapsed_time(self) -> float:
        return self.assigned_duration - self.time_left

    def elapse(self, time: float):
        return self.model_copy(
            update={"time_left": self.time_left - time},
        )

    def set_time_left(self, time: float):
        return self.model_copy(
            update={"time_left": time, "assigned_duration": time},
        )


class Cooldown(Entity):
    time_left: float

    @property
    def available(self):
        return self.time_left <= 0

    def minimum_time_to_available(self) -> float:
        return max(0, self.time_left)

    def elapse(self, time: float):
        return self.model_copy(
            update={"time_left": self.time_left - time},
        )

    def set_time_left(self, time: float):
        return self.model_copy(
            update={"time_left": time},
        )

    def reduce_by_rate(self, rate: float):
        return self.model_copy(
            update={"time_left": self.time_left * (1 - rate)},
        )

    def reduce_by_value(self, time: float):
        return self.model_copy(
            update={"time_left": self.time_left - time},
        )


class Consumable(Entity):
    """
    "Stackable" cooldown.

    쿨타임이 다 찼면 스택이 하나 쌓이고 다시 쿨타임이 도는 Entity.
    """

    maximum_stack: int
    stack: int
    cooldown_duration: float
    time_left: float

    @property
    def available(self):
        return self.stack > 0

    def get_stack(self) -> int:
        return self.stack

    def elapse(self, time: float):
        time_left = self.time_left - time
        stack = self.stack
        while time_left <= 0:
            time_left += self.cooldown_duration
            stack = min(stack + 1, self.maximum_stack)

        if stack == self.maximum_stack:
            time_left = self.cooldown_duration

        return self.model_copy(
            update={"time_left": time_left, "stack": stack},
        )

    def consume(self):
        return self.model_copy(
            update={"stack": self.stack - 1},
        )


class Cycle(Entity):
    tick: int
    period: int

    def get_tick(self) -> int:
        return self.tick

    def step(self):
        tick = self.tick + 1
        tick = tick % self.period
        return self.model_copy(
            update={"tick": tick},
        )

    def clear(self):
        return self.model_copy(
            update={"tick": 0},
        )


class Periodic(Entity):
    interval_counter: float = 0.0
    interval: float
    time_left: float = 0.0
    count: int = 0

    def enabled(self):
        return self.time_left > 0

    def set_time_left(self, time: float, initial_counter: Optional[float] = None):
        return self.model_copy(
            update={
                "time_left": time,
                "interval_counter": initial_counter
                if initial_counter is not None
                else self.interval,
                "count": 0,
            },
        )

    def set_interval_counter(self, counter: float):
        return self.model_copy(
            update={"interval_counter": counter},
        )

    def elapse(self, time: float):
        if self.time_left <= 0:
            return self, 0

        maximum_elapsed = max(
            0, int((self.time_left - self.interval_counter) // self.interval) + 1
        )

        time_left = self.time_left - time
        interval_counter = self.interval_counter - time
        elapse_count = 0

        while interval_counter <= 0 and elapse_count < maximum_elapsed:
            interval_counter += self.interval
            elapse_count += 1

        return self.model_copy(
            update={
                "time_left": time_left,
                "interval_counter": interval_counter,
                "count": self.count + elapse_count,
            },
        ), elapse_count

    def disable(self):
        return self.model_copy(
            update={"time_left": 0},
        )


class Stack(Entity):
    """
    시간 의존성이 없는 스택.
    """

    stack: int = 0
    maximum_stack: int

    def is_full(self) -> bool:
        return self.stack == self.maximum_stack

    def get_stack(self) -> int:
        return self.stack

    def reset(self, value: int = 0):
        return self.model_copy(
            update={"stack": value},
        )

    def increase(self, value: int = 1):
        return self.model_copy(
            update={"stack": min(self.maximum_stack, self.stack + value)},
        )

    def decrease(self, value: int = 1):
        return self.model_copy(
            update={"stack": self.stack - value},
        )


class Integer(Entity):
    value: int = 0

    def get_value(self) -> int:
        return self.value

    def set_value(self, value: int):
        return self.model_copy(
            update={"value": value},
        )


class LastingStack(Entity):
    """A stack, which includes finite duration."""

    stack: int = 0
    maximum_stack: int
    duration: float
    time_left: float = 0

    def enabled(self) -> bool:
        return self.time_left > 0

    def get_stack(self) -> int:
        return self.stack

    def is_maximum(self) -> bool:
        return self.stack == self.maximum_stack

    def reset(self):
        return self.model_copy(
            update={"stack": 0, "time_left": 0},
        )

    def increase(self, value: int = 1):
        return self.model_copy(
            update={
                "stack": min(self.maximum_stack, self.stack + value),
                "time_left": self.duration,
            },
        )

    def decrease(self, value: int = 1):
        return self.model_copy(
            update={"stack": self.stack - value},
        )

    def elapse(self, time: float):
        time_left = self.time_left - time
        if self.time_left < 0:
            return self.reset()
        else:
            return self.model_copy(
                update={"time_left": time_left},
            )

    def regulate(self, value: int):
        return self.model_copy(
            update={"stack": min(value, self.stack)},
        )


class Keydown(Entity):
    interval: float
    interval_counter: float = 0.0
    time_left: float = -1

    @property
    def running(self) -> bool:
        return self.time_left > 0

    def get_next_delay(self) -> float:
        return min(self.interval_counter, self.time_left)

    def start(self, maximum_keydown_time: float, prepare_delay: float):
        return self.model_copy(
            update={
                "interval_counter": prepare_delay,
                "time_left": maximum_keydown_time,
            },
        )

    def stop(self):
        return self.model_copy(
            update={"time_left": 0},
        )

    def elapse(self, time: float):
        if self.time_left <= 0:
            return self, 0

        interval_counter = self.interval_counter - time
        time_left_counter = self.time_left
        elapse_count = 0

        while interval_counter <= 0 and time_left_counter > 0:
            interval_counter += self.interval
            time_left_counter -= self.interval
            elapse_count += 1

        return (
            self.model_copy(
                update={
                    "interval_counter": interval_counter,
                    "time_left": self.time_left - time,
                },
            ),
            elapse_count,
        )
