from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any, Iterable, List, Optional, Tuple

from simaple.optimizer.step_iterator import Iterator


class DiscreteTarget(metaclass=ABCMeta):
    NO_MAXIMUM_STEP = 999999

    def __init__(self, state_length: int, maximum_step: int = -1):
        self.maximum_step = maximum_step
        if maximum_step == -1:
            self.maximum_step = self.NO_MAXIMUM_STEP

        self.state_length = state_length
        self.state: List[int] = [0 for i in range(state_length)]

    @abstractmethod
    def get_result(self) -> Any:
        ...

    @abstractmethod
    def get_value(self) -> float:
        ...

    @abstractmethod
    def get_cost(self) -> float:
        ...

    @abstractmethod
    def clone(self) -> DiscreteTarget:
        ...

    def set_state(self, state: List[int]):
        self.state = state

    def reset_state(self):
        self.state = [0 for i in range(self.state_length)]

    def get_stepped_target(self, steps: Iterable[int]) -> Optional[DiscreteTarget]:
        new_state = list(self.state)
        for step in steps:
            new_state[step] += 1
            if new_state[step] > self.maximum_step:
                return None

        new_target = self.clone()
        new_target.set_state(new_state)

        return new_target


class StepwizeOptimizer:
    NO_TARGET_REWARD = -999
    COST_EXCEED = -999
    INITIAL_REWARD = -1

    class MaximumOptimizationStepExceed(Exception):
        ...

    def __init__(
        self,
        target_prototype: DiscreteTarget,
        maximum_cost: int,
        step_size: int = 2,
        maximum_iteration_count=999,
    ):
        # step_size larger than 2 is EXTREMELY expensive. Be careful.
        self.step_size = step_size
        self.target_prototype = target_prototype
        self.maximum_cost = maximum_cost
        self._maximum_iteration_count = maximum_iteration_count

    def get_increment_iterator(self) -> Iterable[Any]:
        return Iterator().cumulated_iterator(
            self.target_prototype.state_length, self.step_size
        )

    def get_reward(
        self,
        target: DiscreteTarget,
        increments: Tuple,
        original_cost: Optional[float] = None,
        original_value: Optional[float] = None,
    ):
        # Caching
        if original_cost is None:
            original_cost = target.get_cost()
        if original_value is None:
            original_value = target.get_value()

        new_target = target.get_stepped_target(increments)
        if new_target is None:
            return StepwizeOptimizer.NO_TARGET_REWARD

        cost = new_target.get_cost()
        if cost > self.maximum_cost:
            return StepwizeOptimizer.COST_EXCEED

        value = new_target.get_value()

        total_increment = value / original_value - 1
        return total_increment / (cost - original_cost)

    def optimize(self) -> DiscreteTarget:
        target = self.target_prototype.clone()
        iteration_count = 0

        while True:
            optimal_increments = self.get_optimal_increment(target)
            if len(optimal_increments) == 0:
                break

            new_target = target.get_stepped_target(optimal_increments)
            if new_target is None:
                raise TypeError

            target = new_target

            # While phrase protection logic
            iteration_count += 1
            if iteration_count > self._maximum_iteration_count:
                raise StepwizeOptimizer.MaximumOptimizationStepExceed()

        return target

    def get_optimal_increment(self, target: DiscreteTarget) -> Tuple:
        original_cost = target.get_cost()
        original_value = target.get_value()

        best_increments: Tuple = tuple()
        best_reward = StepwizeOptimizer.INITIAL_REWARD

        for increments in self.get_increment_iterator():
            reward = self.get_reward(
                target,
                increments,
                original_cost=original_cost,
                original_value=original_value,
            )
            if reward > best_reward:
                best_reward = reward
                best_increments = increments

        return best_increments
