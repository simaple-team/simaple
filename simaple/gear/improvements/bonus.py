import enum
import math
from typing import Annotated, Literal, Set, Tuple

from pydantic import conint

from simaple.core import Stat
from simaple.core.base import BaseStatType, StatProps, AttackType
from simaple.gear.gear import Gear
from simaple.gear.gear_type import GearType
from simaple.gear.improvements.base import GearImprovement


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


class Bonus(GearImprovement):
    type: Literal["bonus"] = "bonus"
    grade: Annotated[int, conint(ge=1, le=7)]

    def calculate_improvement(self, gear: Gear) -> Stat:
        if gear.boss_reward and self.grade < 3:
            raise ValueError("boss reward cannot assigned less than 3")


class SingleStatBonus(Bonus):
    stat_type: BaseStatType

    def calculate_improvement(self, gear: Gear) -> Stat:
        basis = (gear.req_level // 20 + 1)
        increment = basis * self.grade

        return Stat.parse_obj({self.stat_type.value: increment})


class DoubleStatBonus(Bonus):
    stat_type_pair: Tuple[BaseStatType, BaseStatType]

    def calculate_improvement(self, gear: Gear) -> Stat:
        first_type, second_type = self.stat_type_pair
        basis = (gear.req_level // 40 + 1)
        increment = basis * self.grade

        return Stat.parse_obj({first_type.value: increment, second_type.value: increment})


class AllstatBonus(Bonus):
    def calculate_improvement(self, gear: Gear) -> Stat:
        return Stat.all_stat_multiplier(self.grade)


class BossDamageMultiplierBonus(Bonus):
    def calculate_improvement(self, gear: Gear) -> Stat:
        return Stat(boss_damage_multiplier=self.grade * 2)


class DamageMultiplierBonus(Bonus):
    def calculate_improvement(self, gear: Gear) -> Stat:
        return Stat(damage_multiplier=self.grade)


class ResourcePointBonus(Bonus):
    stat_type: Literal["MHP", "MMP"]

    def calculate_improvement(self, gear: Gear) -> Stat:
        return Stat.parse_obj(
            {self.stat_type: gear.req_level // 10 * 30 * self.grade}
        )


class AttackTypeBonus(Bonus):
    attack_type: AttackType

    def calculate_improvement(self, gear: Gear) -> Stat:
        if gear.is_weapon():
            grade_multiplier = (
                [0, 0, 1, 1.4666, 2.0166, 2.663, 3.4166]
                if gear.boss_reward
                else [1, 2.222, 3.63, 5.325, 7.32, 8.777, 10.25]
            )

            basis = (
                gear.stat.attack_power
                if gear.stat.attack_power > gear.stat.magic_attack
                else gear.stat.magic_attack
            )

            if gear.type in (GearType.sword_zb, GearType.sword_zl):
                if gear.type == GearType.sword_zl:
                    if basis == 100:
                        basis = 102
                    elif basis == 103:
                        basis = 105
                    elif basis == 105:
                        basis = 107
                    elif basis == 112:
                        basis = 114
                    elif basis == 117:
                        basis = 121
                    elif basis == 135:
                        basis = 139
                    elif basis == 169:
                        basis = 173
                    elif basis == 203:
                        basis = 207
                    elif basis == 293:
                        basis = 297
                    elif basis == 337:
                        basis = 342
                    else:
                        print("Not implemented weapon:\n" + str(gear))
                level_multiplier = (
                    6
                    if gear.req_level > 180
                    else (
                        5
                        if gear.req_level > 160
                        else (4 if gear.req_level > 110 else 3)
                    )
                )
            else:
                if gear.boss_reward:
                    level_multiplier = (
                        18
                        if gear.req_level > 160
                        else (
                            15
                            if gear.req_level > 150
                            else (12 if gear.req_level > 110 else 9)
                        )
                    )
                else:
                    level_multiplier = 4 if gear.req_level > 110 else 3

            value = math.ceil(
                basis * grade_multiplier[self.grade - 1] * level_multiplier / 100
            )
        else:
            value = self.grade

        return Stat.parse_obj({self.attack_type.value: value})


class BonusFactory:
    def __init__(self):
        self._bonus_prototypes = {
            BonusType.STR: SingleStatBonus(stat_type=BaseStatType.STR, grade=1),
            BonusType.LUK: SingleStatBonus(stat_type=BaseStatType.LUK, grade=1),
            BonusType.DEX: SingleStatBonus(stat_type=BaseStatType.DEX, grade=1),
            BonusType.INT: SingleStatBonus(stat_type=BaseStatType.INT, grade=1),

            BonusType.STR_DEX: DoubleStatBonus(stat_type_pair=[BaseStatType.STR, BaseStatType.DEX], grade=1),
            BonusType.STR_INT: DoubleStatBonus(stat_type_pair=[BaseStatType.STR, BaseStatType.INT], grade=1),
            BonusType.STR_LUK: DoubleStatBonus(stat_type_pair=[BaseStatType.STR, BaseStatType.LUK], grade=1),
            BonusType.DEX_INT: DoubleStatBonus(stat_type_pair=[BaseStatType.DEX, BaseStatType.INT], grade=1),
            BonusType.DEX_LUK: DoubleStatBonus(stat_type_pair=[BaseStatType.DEX, BaseStatType.LUK], grade=1),
            BonusType.INT_LUK: DoubleStatBonus(stat_type_pair=[BaseStatType.INT, BaseStatType.LUK], grade=1),

            BonusType.all_stat_multiplier: AllstatBonus(grade=1),
            BonusType.boss_damage_multiplier: BossDamageMultiplierBonus(grade=1),
            BonusType.damage_multiplier: DamageMultiplierBonus(grade=1),

            BonusType.MHP: ResourcePointBonus(stat_type="MHP", grade=1),
            BonusType.MMP: ResourcePointBonus(stat_type="MMP", grade=1),
            BonusType.attack_power: AttackTypeBonus(attack_type=AttackType.attack_power, grade=1),
            BonusType.magic_attack: AttackTypeBonus(attack_type=AttackType.magic_attack, grade=1),
        }

    def create(self, bonus_type: BonusType, grade: int) -> Bonus:
        if bonus_type not in self._bonus_prototypes:
            return Bonus(bonus_type=bonus_type, grade=grade)

        bonus_prototype = self._bonus_prototypes[bonus_type]
        bonus = bonus_prototype.copy()
        bonus.grade = grade
        
        return bonus
