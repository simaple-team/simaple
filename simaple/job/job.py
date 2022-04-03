from abc import ABCMeta
from typing import Type, Callable

from pydantic import BaseModel

from simaple.core.damage import DamageLogic
from simaple.job.passive_skill import PassiveSkillset
from simaple.job.description import GeneralJobArgument


class Job(BaseModel, metaclass=ABCMeta):
    class Config:
        arbitrary_types_allowed = True

    passive_skillset: PassiveSkillset
    default_active_skillset: PassiveSkillset
    damage_logic_template: Callable[GeneralJobArgument, DamageLogic]
