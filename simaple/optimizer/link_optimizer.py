from __future__ import annotations

from typing import List, Optional

from simaple.core.jobtype import JobType
from simaple.link import LinkSkillset
from simaple.optimizer.optimizer import DiscreteTarget


class LinkSkillTarget(DiscreteTarget):
    def __init__(
        self,
        default_stat,
        job,
        preempted_jobs: List[JobType],
        armor: int = 300,
        link_skillset: Optional[LinkSkillset] = None,
    ):
        super().__init__(LinkSkillset.get_length(), maximum_step=1)
        self.preempted_jobs = preempted_jobs
        self.default_stat = default_stat
        self.job = job
        self.armor = armor

        if link_skillset is None:
            self._link_skillset = LinkSkillset()
        else:
            self._link_skillset = link_skillset

        self.initialize_state_from_preempted_jobs(preempted_jobs)

    def initialize_state_from_preempted_jobs(self, preempted_jobs: List[JobType]):
        for job in preempted_jobs:
            self.state[self._link_skillset.get_index(job)] = 1

    def get_value(self) -> float:
        resulted_stat = self.default_stat + self._link_skillset.get_stat(self.state)
        return self.job.get_damage_factor(resulted_stat, armor=self.armor)

    def get_cost(self) -> float:
        return sum(self.state)

    def clone(self) -> LinkSkillTarget:
        target = LinkSkillTarget(
            default_stat=self.default_stat,
            job=self.job,
            preempted_jobs=list(self.preempted_jobs),
            link_skillset=self._link_skillset,
        )
        target.set_state(self.state)

        return target
