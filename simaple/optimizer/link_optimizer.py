from __future__ import annotations

from typing import List, Optional

from simaple.core import DamageLogic, JobType, Stat
from simaple.link import LinkSkillset
from simaple.optimizer.optimizer import DiscreteTarget


class LinkSkillTarget(DiscreteTarget):
    def __init__(
        self,
        default_stat: Stat,
        damage_logic: DamageLogic,
        preempted_jobs: List[JobType],
        armor: int = 300,
        candidate_link_skillset: Optional[LinkSkillset] = None,
    ):
        super().__init__(LinkSkillset.get_length(), maximum_step=1)
        self.preempted_jobs = preempted_jobs
        self.default_stat = default_stat
        self.damage_logic = damage_logic
        self.armor = armor

        if candidate_link_skillset is None:
            self._candidate_link_skillset = LinkSkillset()
        else:
            self._candidate_link_skillset = candidate_link_skillset

        self.initialize_state_from_preempted_jobs(preempted_jobs)

    def initialize_state_from_preempted_jobs(self, preempted_jobs: List[JobType]):
        for job in preempted_jobs:
            self.state[self._candidate_link_skillset.get_index(job)] = 1

    def get_value(self) -> float:
        resulted_stat = (
            self.default_stat
            + self._candidate_link_skillset.get_masked(self.state).get_stat()
        )
        return self.damage_logic.get_damage_factor(resulted_stat, armor=self.armor)

    def get_cost(self) -> float:
        return sum(self.state)

    def clone(self) -> LinkSkillTarget:
        target = LinkSkillTarget(
            default_stat=self.default_stat,
            damage_logic=self.damage_logic,
            preempted_jobs=list(self.preempted_jobs),
            candidate_link_skillset=self._candidate_link_skillset,
        )
        target.set_state(self.state)

        return target

    def get_result(self) -> LinkSkillset:
        return self._candidate_link_skillset.get_masked(self.state)
