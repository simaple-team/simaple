from __future__ import annotations

from simaple.core import Stat
from simaple.hyperstat import Hyperstat
from simaple.job.job import Job
from simaple.optimizer.optimizer import DiscreteTarget


class HyperstatTarget(DiscreteTarget):
    def __init__(self, default_stat: Stat, job: Job, armor=300, hyperstat_prototype: Optional[Hyperstat] = None):
        super().__init__(Hyperstat.length())
        self.default_stat = default_stat
        self.job = job
        self.armor = armor

        if hyperstat_prototype is None:
            self._hyperstat_prototype = Hyperstat()
        else:
            self._hyperstat_prototype = hyperstat_prototype

    def get_value(self) -> float:
        hyperstat = Hyperstat(
            options=self._hyperstat_prototype.options,
            cost=self._hyperstat_prototype.cost,
            levels=self.state
        )

        resulted_stat = self.default_stat + hyperstat.get_stat()
        return self.job.get_damage_factor(resulted_stat, armor=self.armor)

    def get_cost(self) -> float:
        hyperstat = Hyperstat(
            options=self._hyperstat_prototype.options,
            cost=self._hyperstat_prototype.cost,
            levels=self.state
        )

        return hyperstat.get_current_cost()

    def clone(self) -> HyperstatTarget:
        target = HyperstatTarget(
            default_stat=self.default_stat,
            job=self.job,
            hyperstat_prototype=self._hyperstat_prototype
        )
        target.set_state(self.state)

        return target

    def get_result(self) -> Hyperstat:
        return Hyperstat(levels=self.state)
