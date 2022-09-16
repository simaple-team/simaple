from abc import ABCMeta, abstractmethod
from typing import List

from pydantic import BaseModel

from simaple.core import Stat
from simaple.job.passive_skill import PassiveSkill


class StaticPropertyInterface(BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def get_default_stat(self) -> Stat:
        ...


class StaticProperty(StaticPropertyInterface):
    class Config:
        arbitrary_types_allowed = False

    passive_skillset: List[PassiveSkill]
    default_active_skillset: List[PassiveSkill]

    def get_default_stat(self) -> Stat:
        return sum(
            [
                passive_skill.stat
                for passive_skill in self.passive_skillset
                + self.default_active_skillset
            ],
            Stat(),
        )
