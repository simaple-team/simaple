import enum

from pydantic import BaseModel

from simaple.core.base import AttackType, BaseStatType
from simaple.gear.improvements.bonus import (
    AllstatBonus,
    AttackTypeBonus,
    Bonus,
    BossDamageMultiplierBonus,
    DamageMultiplierBonus,
    DualStatBonus,
    ResourcePointBonus,
    SingleStatBonus,
)


class BonusType(enum.Enum):
    all_stat_multiplier = "all_stat_multiplier"

    STR = "STR"
    DEX = "DEX"
    INT = "INT"
    LUK = "LUK"

    STR_DEX = "STR_DEX"
    STR_INT = "STR_INT"
    STR_LUK = "STR_LUK"
    DEX_INT = "DEX_INT"
    DEX_LUK = "DEX_LUK"
    INT_LUK = "INT_LUK"

    MMP = "MMP"
    MHP = "MHP"

    magic_attack = "magic_attack"
    attack_power = "attack_power"

    boss_damage_multiplier = "boss_damage_multiplier"
    damage_multiplier = "damage_multiplier"

    @classmethod
    def refine_double_key(cls, maybe_reversed: str):
        for bonus_type in (
            BonusType.STR_DEX,
            BonusType.STR_INT,
            BonusType.STR_LUK,
            BonusType.DEX_INT,
            BonusType.DEX_LUK,
            BonusType.INT_LUK,
        ):
            reversed_key = "_".join(reversed(bonus_type.value.split("_")))
            if maybe_reversed == reversed_key:
                return bonus_type.value

        return maybe_reversed


class BonusSpec(BaseModel):
    bonus_type: BonusType
    grade: int


class BonusFactory:
    def __init__(self):
        self._bonus_prototypes = {
            BonusType.STR: SingleStatBonus(stat_type=BaseStatType.STR, grade=1),
            BonusType.LUK: SingleStatBonus(stat_type=BaseStatType.LUK, grade=1),
            BonusType.DEX: SingleStatBonus(stat_type=BaseStatType.DEX, grade=1),
            BonusType.INT: SingleStatBonus(stat_type=BaseStatType.INT, grade=1),
            BonusType.STR_DEX: DualStatBonus(
                stat_type_pair=[BaseStatType.STR, BaseStatType.DEX], grade=1
            ),
            BonusType.STR_INT: DualStatBonus(
                stat_type_pair=[BaseStatType.STR, BaseStatType.INT], grade=1
            ),
            BonusType.STR_LUK: DualStatBonus(
                stat_type_pair=[BaseStatType.STR, BaseStatType.LUK], grade=1
            ),
            BonusType.DEX_INT: DualStatBonus(
                stat_type_pair=[BaseStatType.DEX, BaseStatType.INT], grade=1
            ),
            BonusType.DEX_LUK: DualStatBonus(
                stat_type_pair=[BaseStatType.DEX, BaseStatType.LUK], grade=1
            ),
            BonusType.INT_LUK: DualStatBonus(
                stat_type_pair=[BaseStatType.INT, BaseStatType.LUK], grade=1
            ),
            BonusType.all_stat_multiplier: AllstatBonus(grade=1),
            BonusType.boss_damage_multiplier: BossDamageMultiplierBonus(grade=1),
            BonusType.damage_multiplier: DamageMultiplierBonus(grade=1),
            BonusType.MHP: ResourcePointBonus(stat_type="MHP", grade=1),
            BonusType.MMP: ResourcePointBonus(stat_type="MMP", grade=1),
            BonusType.attack_power: AttackTypeBonus(
                attack_type=AttackType.attack_power, grade=1
            ),
            BonusType.magic_attack: AttackTypeBonus(
                attack_type=AttackType.magic_attack, grade=1
            ),
        }

    def create(self, bonus_type: BonusType, grade: int) -> Bonus:
        if bonus_type not in self._bonus_prototypes:
            raise ValueError

        bonus_prototype: Bonus = self._bonus_prototypes[bonus_type]
        bonus = bonus_prototype.copy()
        bonus.grade = grade

        return bonus
