from abc import ABC, abstractmethod

from simaple.core import ExtendedStat, JobType, Stat
from simaple.gear.gear import Gear
from simaple.gear.symbol_gear import SymbolGear
from simaple.request.service.util import BestStatSelector
from simaple.system.artifact import Artifact
from simaple.system.hexa_stat import HexaStat
from simaple.system.hyperstat import Hyperstat
from simaple.system.link import LinkSkillset
from simaple.system.propensity import Propensity
from simaple.system.union import UnionSquad


class AbilityLoader(ABC):
    @abstractmethod
    def load_stat(self, character_name: str) -> ExtendedStat:
        pass

    @abstractmethod
    def load_best_stat(
        self, character_name: str, selector: BestStatSelector
    ) -> ExtendedStat:
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

    @abstractmethod
    def load_best_union_stat(
        self, character_name: str, selector: BestStatSelector
    ) -> ExtendedStat:
        """
        UnionSquad, UnionOccupationStat을 종합하여 제일 좋은 스탯을 반환합니다.
        """
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

    @abstractmethod
    def get_combat_power_weapon_replacement(self, character_name: str) -> Stat:
        ...


class CharacterBasicLoader(ABC):
    @abstractmethod
    def load_character_level(self, character_name: str) -> int:
        pass

    @abstractmethod
    def load_character_ap_based_stat(self, character_name: str) -> Stat:
        pass

    @abstractmethod
    def load_character_job_type(self, character_name: str) -> JobType:
        pass


class LinkSkillLoader(ABC):
    @abstractmethod
    def load_link_skill(self, character_name: str) -> LinkSkillset:
        pass


class CharacterSkillLoader(ABC):
    @abstractmethod
    def load_character_passive_stat(
        self, character_name: str, character_level: int
    ) -> ExtendedStat:
        pass

    @abstractmethod
    def load_character_hexa_stat(
        self,
        character_name: str,
    ) -> HexaStat:
        pass

    @abstractmethod
    def load_zero_grade_skill_passive_stat(
        self,
        character_name: str,
    ) -> tuple[ExtendedStat, bool]:
        """
        0차 스킬로부터 얻는 패시브 스탯을 반환합니다.
        더불어, 해방 무기 장착 여부도 반환합니다.
        """
        pass

    @abstractmethod
    def load_combat_power_related_stat(
        self,
        character_name: str,
    ) -> tuple[ExtendedStat, bool]:
        """
        전투력 계산에 포함되는 0차 스킬의 효과 총계를 반환합니다.
        더불어, 해방 무기 장착 여부도 반환합니다.
        """
        pass

    @abstractmethod
    def load_hexa_skill_levels(
        self, character_name: str
    ) -> tuple[dict[str, int], dict[str, int]]:
        """
        헥사스킬 레벨을 반환합니다.
        각각 헥사스킬, 헥사 강화(5차 스킬 강화) 레벨을 반환합니다.
        """
        pass
