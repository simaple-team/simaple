from abc import ABCMeta
from typing import List

from pydantic import BaseModel

from simaple.core.damage import DamageLogic
from simaple.job.passive_skill import PassiveSkill


class Job(BaseModel, metaclass=ABCMeta):
    passive_skills: List[PassiveSkill]
    damage_logic: DamageLogic
