from abc import ABCMeta, abstractmethod
from typing import List
from pydantic import BaseModel

from simaple.core import Stat
from simaple.job.passive_skill import PassiveSkill
from simaple.core.damage import DamageLogic

class Job(BaseModel, metaclass=ABCMeta):
    passive_skills: List[PassiveSkill]
    damage_logic: DamageLogic
