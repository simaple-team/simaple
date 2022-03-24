from __future__ import annotations

from simaple.core import Stat
from simaple.hyperstat import Hyperstat
from simaple.job.job import Job
from simaple.optimizer.optimizer import DiscreteTarget


class HyperstatTarget(DiscreteTarget):
    def __init__(self, default_stat: Stat, job: Job, armor=300):
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

    def clone(self) -> HyperstatTarget:
        target = HyperstatTarget(
            default_stat=self.default_stat,
            job=self.job,
        )
        target.set_state(self.state)

        return target
