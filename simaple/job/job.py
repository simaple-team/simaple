from abc import ABCMeta

from pydantic import BaseModel

from simaple.core.damage import DamageLogic
from simaple.job.passive_skill import PassiveSkillset


class Job(BaseModel, metaclass=ABCMeta):
    passive_skillset: PassiveSkillset
    default_active_skillset: PassiveSkillset
    damage_logic: DamageLogic
