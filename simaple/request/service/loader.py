from abc import ABC, abstractmethod

from simaple.core import ExtendedStat, Stat
from simaple.gear.gear import Gear
from simaple.gear.symbol_gear import SymbolGear
from simaple.system.artifact import Artifact
from simaple.system.hyperstat import Hyperstat
from simaple.system.link import LinkSkillset
from simaple.system.propensity import Propensity
from simaple.system.union import UnionSquad


class AbilityLoader(ABC):
    @abstractmethod
    def load_stat(self, character_name: str) -> ExtendedStat:
        pass


class PropensityLoader(ABC):
    @abstractmethod
    def load_propensity(self, character_name: str) -> Propensity:
        pass


class HyperstatLoader(ABC):
    @abstractmethod
    def load_hyper_stat(self, character_name: str) -> Hyperstat:
        pass


class UnionLoader(ABC):
    @abstractmethod
    def load_union_squad(self, character_name: str) -> UnionSquad:
        pass

    @abstractmethod
    def load_union_squad_effect(self, character_name: str) -> ExtendedStat:
        pass

    @abstractmethod
    def load_union_artifact(self, character_name: str) -> Artifact:
        pass

    @abstractmethod
    def load_union_occupation_stat(self, character_name: str) -> ExtendedStat:
        pass


class GearLoader(ABC):
    @abstractmethod
    def load_equipments(self, character_name: str) -> list[tuple[Gear, str]]:
        pass

    @abstractmethod
    def load_symbols(self, character_name: str) -> list[SymbolGear]:
        pass

    @abstractmethod
    def load_pet_equipments_stat(self, character_name: str) -> Stat:
        pass

    @abstractmethod
    def load_gear_related_stat(self, character_name: str) -> ExtendedStat:
        pass


class CharacterBasicLoader(ABC):
    @abstractmethod
    def load_character_level(self, character_name: str) -> int:
        pass

    @abstractmethod
    def load_character_ap_based_stat(self, character_name: str) -> Stat:
        pass


class LinkSkillLoader(ABC):
    @abstractmethod
    def load_link_skill(self, character_name: str) -> LinkSkillset:
        pass
