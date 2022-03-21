from __future__ import annotations

from typing import List, Optional

from simaple.core.jobtype import JobType
from simaple.optimizer.optimizer import StepwizeOptimizationTarget
from simaple.union import UnionBlockstat


class UnionBlockStepwizeOptimizationTarget(StepwizeOptimizationTarget):
    def __init__(
        self,
        default_stat,
        job,
        preempted_jobs: List[JobType],
        armor: int = 300,
        union_blocks: Optional[UnionBlockstat] = None,
    ):
        super().__init__(UnionBlockstat.get_length(), maximum_step=1)
        self.preempted_jobs = preempted_jobs
        self.default_stat = default_stat
        self.job = job
        self.armor = armor

        if union_blocks is None:
            self._union_blocks = UnionBlockstat.create_with_some_large_blocks(
                self.preempted_jobs
            )
        else:
            self._union_blocks = union_blocks

        self.initialize_state_from_preempted_jobs(preempted_jobs)

    def initialize_state_from_preempted_jobs(self, preempted_jobs: List[JobType]):
        for job in preempted_jobs:
            self.state[self._union_blocks.get_index(job)] = 1

    def get_value(self) -> float:
        resulted_stat = self.default_stat + self._union_blocks.get_stat(self.state)
        return self.job.get_damage_factor(resulted_stat, armor=self.armor)

    def get_cost(self) -> float:
        return sum(self.state)

    def clone(self) -> UnionBlockStepwizeOptimizationTarget:
        target = UnionBlockStepwizeOptimizationTarget(
            default_stat=self.default_stat,
            job=self.job,
            preempted_jobs=list(self.preempted_jobs),
            union_blocks=self._union_blocks,
        )
        target.set_state(self.state)

        return target
