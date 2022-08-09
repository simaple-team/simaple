import enum
from abc import ABCMeta, abstractmethod
from typing import List, Union

from pydantic import BaseModel, Extra, Field

from simaple.core import ActionStat, LevelStat, Stat


class PotentialTier(enum.IntEnum):
    empty = -1
    normal = 0
    rare = 1
    epic = 2
    unique = 3
    legendary = 4


class PotentialInterface(BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def get_stat(self, level: int = 0) -> Stat:
        ...

    @abstractmethod
    def get_action_stat(self) -> ActionStat:
        ...


class AbstractPotential(PotentialInterface):
    class Config:
        extra = Extra.forbid

    options: List[Union[Stat, ActionStat, LevelStat]] = Field(default_factory=list)

    def get_stat(self, level: int = 0) -> Stat:
        stat = Stat()
        for option in self.options:
            if isinstance(option, Stat):
                stat += option
            if isinstance(option, LevelStat):
                stat += option.get_stat(level=level)

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
