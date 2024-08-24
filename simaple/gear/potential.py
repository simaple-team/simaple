import enum
from abc import ABCMeta, abstractmethod
from typing import List

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
    def get_stat(self, level: int = 0) -> Stat: ...

    @abstractmethod
    def get_action_stat(self) -> ActionStat: ...

    @abstractmethod
    def get_level_stat(self) -> LevelStat: ...


class Potential(PotentialInterface):
    options: List[ExtendedStat] = []

    def _get_extended_stat(self) -> ExtendedStat:
        extended_stat = ExtendedStat()
        for option in self.options:
            extended_stat += option

        return extended_stat

    def get_stat(self, level: int = 0) -> Stat:
        return self._get_extended_stat().stat

    def get_action_stat(self) -> ActionStat:
        return self._get_extended_stat().action_stat

    def get_level_stat(self) -> LevelStat:
        return self._get_extended_stat().level_stat
