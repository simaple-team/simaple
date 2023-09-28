import enum
from abc import ABCMeta, abstractmethod
from typing import List, Union

from pydantic import BaseModel

from simaple.core import ActionStat, ExtendedStat, LevelStat, Stat


class PotentialTier(enum.Enum):
    empty = "empty"
    normal = "normal"
    rare = "rare"
    epic = "epic"
    unique = "unique"
    legendary = "legendary"


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
    options: List[Union[Stat, ActionStat, LevelStat]] = []

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
