import enum
import math
from typing import Annotated, Literal

from pydantic import conint

from simaple.core import Stat
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


class Bonus(GearImprovement):
    type: Literal["bonus"] = "bonus"
    grade: Annotated[int, conint(ge=1, le=7)]
    bonus_type: BonusType

    def calculate_improvement(self, gear: Gear) -> Stat:
        if gear.boss_reward and self.grade < 3:
            raise ValueError("boss reward cannot assigned less than 3")

        if self.bonus_type == BonusType.all_stat_multiplier:
            return Stat.all_stat_multiplier(self.grade)

        if self.bonus_type in (
            BonusType.STR,
            BonusType.DEX,
            BonusType.INT,
            BonusType.LUK,
        ):
            value = (gear.req_level // 20 + 1) * self.grade
            return Stat.parse_obj({self.bonus_type.value: value})

        if self.bonus_type in (
            BonusType.STR_DEX,
            BonusType.STR_INT,
            BonusType.STR_LUK,
            BonusType.DEX_INT,
            BonusType.DEX_LUK,
            BonusType.INT_LUK,
        ):
            value = (gear.req_level // 40 + 1) * self.grade
            ability_a, ability_b = str(self.bonus_type.value).split("_")

            return Stat.parse_obj({ability_a: value, ability_b: value})

        if self.bonus_type == BonusType.boss_damage_multiplier:
            return Stat(boss_damage_multiplier=self.grade * 2)

        if self.bonus_type == BonusType.damage_multiplier:
            return Stat(damage_multiplier=self.grade)

        if self.bonus_type in (BonusType.MHP, BonusType.MMP):
            return Stat.parse_obj(
                {self.bonus_type.value: gear.req_level // 10 * 30 * self.grade}
            )

        if self.bonus_type in (BonusType.attack_power, BonusType.magic_attack):
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

            return Stat.parse_obj({self.bonus_type.value: value})

        raise TypeError
