from abc import ABCMeta, abstractmethod

from pydantic import BaseModel

from simaple.core.base import AttackType, BaseStatType, Stat


class DamageLogic(BaseModel, metaclass=ABCMeta):
    attack_range_constant: float
    mastery: float

    @abstractmethod
    def get_base_stat_factor(self, stat: Stat) -> float:
        ...

    @abstractmethod
    def get_major_stat(self, stat: Stat) -> float:
        ...

    @abstractmethod
    def get_attack_type_factor(self, stat: Stat) -> float:
        ...

    def get_maximum_attack_range(self, stat: Stat) -> float:
        return (
            (1 + (stat.boss_damage_multiplier) * 0.01)
            * (1 + 0.01 * stat.final_damage_multiplier)
            * self.get_base_stat_factor(stat)
            * self.get_attack_type_factor(stat)
            * self.attack_range_constant
        )

    def get_minimum_attack_range(self, stat: Stat) -> float:
        return self.get_maximum_attack_range(stat) * self.mastery

    def get_general_damage_factor(self, stat: Stat) -> float:
        return (1 + (stat.boss_damage_multiplier + stat.damage_multiplier) * 0.01) * (
            1 + 0.01 * stat.final_damage_multiplier
        )

    def get_armor_factor(self, stat: Stat, armor: int) -> float:
        return 1 - 0.0001 * (armor * (100 - stat.ignored_defence))

    def get_critical_factor(self, stat: Stat) -> float:
        return 1 + (35 + stat.critical_damage) * min(100, stat.critical_rate) * 0.0001

    def get_damage_factor(self, stat: Stat, armor: int = 300) -> float:
        return (
            self.get_general_damage_factor(stat)
            * self.get_armor_factor(stat, armor)
            * self.get_critical_factor(stat)
            * self.get_base_stat_factor(stat)
            * self.get_attack_type_factor(stat)
        )


class STRBasedDamageLogic(DamageLogic):
    def get_major_stat(self, stat: Stat) -> float:
        return stat.get_base_stat_coefficient(BaseStatType.STR)

    def get_base_stat_factor(self, stat: Stat) -> float:
        return stat.get_base_stat_coefficient(
            BaseStatType.STR
        ) * 4 + stat.get_base_stat_coefficient(BaseStatType.DEX)

    def get_attack_type_factor(self, stat: Stat) -> float:
        return stat.get_attack_coefficient(AttackType.attack_power)


class INTBasedDamageLogic(DamageLogic):
    def get_major_stat(self, stat: Stat) -> float:
        return stat.get_base_stat_coefficient(BaseStatType.INT)

    def get_base_stat_factor(self, stat: Stat) -> float:
        return stat.get_base_stat_coefficient(
            BaseStatType.INT
        ) * 4 + stat.get_base_stat_coefficient(BaseStatType.LUK)

    def get_attack_type_factor(self, stat: Stat) -> float:
        return stat.get_attack_coefficient(AttackType.magic_attack)


class DEXBasedDamageLogic(DamageLogic):
    def get_major_stat(self, stat: Stat) -> float:
        return stat.get_base_stat_coefficient(BaseStatType.DEX)

    def get_base_stat_factor(self, stat: Stat) -> float:
        return stat.get_base_stat_coefficient(
            BaseStatType.DEX
        ) * 4 + stat.get_base_stat_coefficient(BaseStatType.STR)

    def get_attack_type_factor(self, stat: Stat) -> float:
        return stat.get_attack_coefficient(AttackType.attack_power)


class LUKBasedDamageLogic(DamageLogic):
    def get_major_stat(self, stat: Stat) -> float:
        return stat.get_base_stat_coefficient(BaseStatType.LUK)

    def get_base_stat_factor(self, stat: Stat) -> float:
        return stat.get_base_stat_coefficient(
            BaseStatType.LUK
        ) * 4 + stat.get_base_stat_coefficient(BaseStatType.DEX)

    def get_attack_type_factor(self, stat: Stat) -> float:
        return stat.get_attack_coefficient(AttackType.attack_power)
