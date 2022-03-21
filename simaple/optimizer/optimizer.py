from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Iterable, List, Optional, Tuple

from simaple.hyperstat import Hyperstat
from simaple.optimizer.step_iterator import Iterator


class StepwizeOptimizationTarget(metaclass=ABCMeta):
    NO_MAXIMUM_STEP = 999999

    def __init__(self, state_length, maximum_step=-1):
        self.maximum_step = maximum_step
        if maximum_step == -1:
            self.maximum_step = self.NO_MAXIMUM_STEP

        self.state_length = state_length
        self.state: List[int] = [0 for i in range(state_length)]

    @abstractmethod
    def get_value(self) -> float:
        ...

    @abstractmethod
    def get_cost(self) -> float:
        ...

    @abstractmethod
    def clone(self):
        ...

    def set_state(self, state: List[int]):
        self.state = state

    def reset_state(self):
        self.state = [0 for i in range(self.state_length)]

    def get_stepped_target(
        self, steps: Iterable[int]
    ) -> Optional[StepwizeOptimizationTarget]:
        new_state = list(self.state)
        for step in steps:
            new_state[step] += 1
            if new_state[step] > self.maximum_step:
                return None

        new_target = self.clone()
        new_target.set_state(new_state)

        return new_target


class HyperstatStepwizeOptimizationTarget(StepwizeOptimizationTarget):
    def __init__(self, default_stat, job, armor=300):
        super().__init__(Hyperstat.length())
        self.default_stat = default_stat
        self.job = job
        self.armor = armor

    def get_value(self) -> float:
        hyperstat = Hyperstat(levels=self.state)

        resulted_stat = self.default_stat + hyperstat.get_stat()
        return self.job.get_damage_factor(resulted_stat, armor=self.armor)

    def get_cost(self) -> float:
        hyperstat = Hyperstat(levels=self.state)

        return hyperstat.get_current_cost()

    def clone(self) -> HyperstatStepwizeOptimizationTarget:
        target = HyperstatStepwizeOptimizationTarget(
            default_stat=self.default_stat,
            job=self.job,
        )
        target.set_state(self.state)

        return target


class StepwizeOptimizer:
    class MaximumOptimizationStepExceed(Exception):
        ...

    def __init__(
        self,
        target_prototype: StepwizeOptimizationTarget,
        maximum_cost: int,
        step_size: int = 2,
        maximum_iteration_count=999,
    ):
        # step_size larger than 2 is EXTREMELY expensive. Be careful.
        self.step_size = step_size
        self.target_prototype = target_prototype
        self.maximum_cost = maximum_cost
        self._maximum_iteration_count = maximum_iteration_count

    def get_increment_iterator(self) -> Iterable:
        return Iterator().cumulated_iterator(
            self.target_prototype.state_length, self.step_size
        )

    def get_reward(self, target, increments, original_cost=None, original_value=None):
        # Caching
        if original_cost is None:
            original_cost = target.get_cost()
        if original_value is None:
            original_value = target.get_value()

        new_target = target.get_stepped_target(increments)
        if new_target is None:
            return 0.0

        cost = new_target.get_cost()
        if cost > self.maximum_cost:
            return 0.0

        value = new_target.get_value()

        total_increment = value / original_value - 1
        return total_increment / (cost - original_cost)

    def optimize(self) -> StepwizeOptimizationTarget:
        target = self.target_prototype.clone()
        iteration_count = 0

        while True:
            optimal_increments = self.get_optimal_increment(target)
            if len(optimal_increments) == 0:
                break

            target = target.get_stepped_target(optimal_increments)
            if target is None:
                raise TypeError

            # While phrase protection logic
            iteration_count += 1
            if iteration_count > self._maximum_iteration_count:
                raise StepwizeOptimizer.MaximumOptimizationStepExceed()

        return target

    def get_optimal_increment(self, target: StepwizeOptimizationTarget) -> Tuple:
        original_cost = target.get_cost()
        original_value = target.get_value()

        best_increments: Tuple = tuple()
        best_reward = 0

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
