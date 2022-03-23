from __future__ import annotations

from simaple.optimizer.optimizer import DiscreteTarget
from simaple.union import UnionOccupationStat


class UnionOccupationTarget(DiscreteTarget):
    def __init__(self, default_stat, job, armor=300):
        super().__init__(UnionOccupationStat.length(), 40)
        self.default_stat = default_stat
        self.job = job
        self.armor = armor

    def get_value(self) -> float:
        union_occupation_stat = UnionOccupationStat(occupation_state=self.state)

        resulted_stat = self.default_stat + union_occupation_stat.get_stat()
        return self.job.get_damage_factor(resulted_stat, armor=self.armor)

    def get_cost(self) -> float:
        return sum(self.state)

    def clone(self) -> UnionOccupationTarget:
        target = UnionOccupationTarget(
            default_stat=self.default_stat,
            job=self.job,
        )
        target.set_state(self.state)

        return target
