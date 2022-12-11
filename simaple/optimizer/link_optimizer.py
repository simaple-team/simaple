from __future__ import annotations

from typing import List

from simaple.core import DamageLogic, JobType, Stat
from simaple.optimizer.optimizer import DiscreteTarget
from simaple.system.link import LinkSkillset


class LinkSkillTarget(DiscreteTarget):
    def __init__(
        self,
        default_stat: Stat,
        damage_logic: DamageLogic,
        link_skillset: LinkSkillset,
        preempted_jobs: List[JobType],
        armor: int = 300,
    ):
        super().__init__(link_skillset.length(), maximum_step=1)
        self.preempted_jobs = preempted_jobs
        self.default_stat = default_stat
        self.damage_logic = damage_logic
        self.armor = armor

        self._link_skillset = link_skillset

        self.initialize_state_from_preempted_jobs(preempted_jobs)

    def initialize_state_from_preempted_jobs(self, preempted_jobs: List[JobType]):
        for job in preempted_jobs:
            self.state[self._link_skillset.get_index(job)] = 1

    def get_value(self) -> float:
        resulted_stat = (
            self.default_stat + self._link_skillset.get_masked(self.state).get_stat()
        )
        return self.damage_logic.get_damage_factor(resulted_stat, armor=self.armor)

    def get_cost(self) -> float:
        return sum(self.state)

    def clone(self) -> LinkSkillTarget:
        target = LinkSkillTarget(
            default_stat=self.default_stat,
            damage_logic=self.damage_logic,
            preempted_jobs=list(self.preempted_jobs),
            link_skillset=self._link_skillset,
        )
        target.set_state(self.state)

        return target

    def get_result(self) -> LinkSkillset:
        return self._link_skillset.get_masked(self.state)
