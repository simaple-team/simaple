from abc import ABCMeta
from typing import List

from pydantic import BaseModel

from simaple.core import Stat
from simaple.core.damage import DamageLogic
from simaple.core.jobtype import JobType
from simaple.job.passive_skill import PassiveSkill


class Job(BaseModel, metaclass=ABCMeta):
    class Config:
        arbitrary_types_allowed = False

    passive_skillset: List[PassiveSkill]
    default_active_skillset: List[PassiveSkill]
    damage_logic: DamageLogic
    level: int
    level_stat: Stat
    type: JobType

    def get_default_stat(self) -> Stat:
        return sum(
            [
                passive_skill.stat
                for passive_skill in self.passive_skillset
                + self.default_active_skillset
            ],
            Stat(),
        )
