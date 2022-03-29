import enum
from typing import List, Union

from pydantic import BaseModel, Field, Extra

from simaple.core import ActionStat, Stat


class PotentialTier(enum.IntEnum):
    empty = -1
    normal = 0
    rare = 1
    epic = 2
    unique = 3
    legendary = 4


class AbstractPotential(BaseModel):
    class Config:
        extra = Extra.forbid

    options: List[Union[Stat, ActionStat]] = Field(default_factory=list)

    def get_stat(self) -> Stat:
        stat = Stat()
        for option in self.options:
            if isinstance(option, Stat):
                stat += option

        return stat

    def get_action_stat(self) -> ActionStat:
        action_stat = ActionStat()
        for option in self.options:
            if isinstance(option, ActionStat):
                action_stat += option

        return action_stat


class Potential(AbstractPotential):
    ...


class AdditionalPotential(AbstractPotential):
    ...
