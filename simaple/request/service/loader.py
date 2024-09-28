from abc import ABC, abstractmethod

from simaple.core import ExtendedStat, Stat
from simaple.system.hyperstat import Hyperstat
from simaple.system.propensity import Propensity
from simaple.system.union import UnionSquad
from simaple.gear.gear import Gear
from simaple.gear.symbol_gear import SymbolGear


class AbilityLoader(ABC):
    @abstractmethod
    async def load_stat(self, character_name: str) -> ExtendedStat:
        pass


class PropensityLoader(ABC):
    @abstractmethod
    async def load_propensity(self, character_name: str) -> Propensity:
        pass


class HyperstatLoader(ABC):
    @abstractmethod
    async def load_hyper_stat(self, character_name: str) -> Hyperstat:
        pass


class UnionLoader(ABC):
    @abstractmethod
    async def load_union_squad(self, character_name: str) -> UnionSquad:
        pass

    @abstractmethod
    async def load_union_squad_effect(self, character_name: str) -> ExtendedStat:
        pass


class GearLoader(ABC):
    @abstractmethod
    async def load_equipments(self, character_name: str) -> list[tuple[Gear, str]]:
        pass

    @abstractmethod
    async def load_symbols(self, character_name: str) -> list[SymbolGear]:
        pass

    @abstractmethod
    async def load_pet_equipments_stat(self, character_name: str) -> Stat:
        pass
