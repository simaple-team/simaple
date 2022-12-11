from __future__ import annotations

from typing import List

from simaple.core import DamageLogic, JobType, Stat
from simaple.optimizer.optimizer import DiscreteTarget
from simaple.system.union import UnionSquad


class UnionSquadTarget(DiscreteTarget):
    def __init__(
        self,
        default_stat: Stat,
        damage_logic: DamageLogic,
        union_squad: UnionSquad,
        preempted_jobs: List[JobType],
        armor: int = 300,
    ):
        super().__init__(union_squad.length(), maximum_step=1)
        self.preempted_jobs = preempted_jobs
        self.default_stat = default_stat
        self.damage_logic = damage_logic
        self.armor = armor
        self._union_squad = union_squad

        self.initialize_state_from_preempted_jobs(preempted_jobs)

    def initialize_state_from_preempted_jobs(self, preempted_jobs: List[JobType]):
        for job in preempted_jobs:
            self.state[self._union_squad.get_index(job)] = 1

    def get_value(self) -> float:
        resulted_stat = (
            self.default_stat + self._union_squad.get_masked(self.state).get_stat()
        )
        return self.damage_logic.get_damage_factor(resulted_stat, armor=self.armor)

    def get_cost(self) -> float:
        return sum(self.state)

    def clone(self) -> UnionSquadTarget:
        target = UnionSquadTarget(
            default_stat=self.default_stat,
            damage_logic=self.damage_logic,
            preempted_jobs=list(self.preempted_jobs),
            union_squad=self._union_squad,
        )
        target.set_state(self.state)

        return target

    def get_result(self) -> UnionSquad:
        return self._union_squad.get_masked(self.state)
