import enum
from abc import ABCMeta, abstractmethod
from typing import List, Union

from pydantic import BaseModel, Extra, Field

from simaple.core import ActionStat, ExtendedStat, LevelStat, Stat


class PotentialTier(enum.IntEnum):
    empty = -1
    normal = 0
    rare = 1
    epic = 2
    unique = 3
    legendary = 4


class PotentialInterface(BaseModel, metaclass=ABCMeta):
    def get_extended_stat(self) -> ExtendedStat:
        return ExtendedStat(
            stat=self.get_stat(),
            action_stat=self.get_action_stat(),
            level_stat=self.get_level_stat(),
        )

    @abstractmethod
    def get_stat(self, level: int = 0) -> Stat:
        ...

    @abstractmethod
    def get_action_stat(self) -> ActionStat:
        ...

    @abstractmethod
    def get_level_stat(self) -> LevelStat:
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

    def get_level_stat(self) -> LevelStat:
        level_stat = LevelStat()
        for option in self.options:
            if isinstance(option, LevelStat):
                level_stat += option

        return level_stat


class Potential(AbstractPotential):
    ...


class AdditionalPotential(AbstractPotential):
    ...
