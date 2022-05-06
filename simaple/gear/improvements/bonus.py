import math
from typing import Annotated, Literal, Tuple

from pydantic import conint

from simaple.core import Stat
from simaple.core.base import AttackType, BaseStatType
from simaple.gear.gear import Gear
from simaple.gear.gear_type import GearType
from simaple.gear.improvements.base import GearImprovement


class Bonus(GearImprovement):
    type: Literal["bonus"] = "bonus"
    grade: Annotated[int, conint(ge=1, le=7)]

    def validate_grade(self, gear: Gear):
        if gear.boss_reward and self.grade < 3:
            raise ValueError("boss reward cannot assigned less than 3")


class SingleStatBonus(Bonus):
    stat_type: BaseStatType

    def calculate_improvement(self, gear: Gear) -> Stat:
        self.validate_grade(gear)
        basis = gear.req_level // 20 + 1
        increment = basis * self.grade

        return Stat.parse_obj({self.stat_type.value: increment})


class DoubleStatBonus(Bonus):
    stat_type_pair: Tuple[BaseStatType, BaseStatType]

    def calculate_improvement(self, gear: Gear) -> Stat:
        self.validate_grade(gear)
        first_type, second_type = self.stat_type_pair
        basis = gear.req_level // 40 + 1
        increment = basis * self.grade

        return Stat.parse_obj(
            {first_type.value: increment, second_type.value: increment}
        )


class AllstatBonus(Bonus):
    def calculate_improvement(self, gear: Gear) -> Stat:
        self.validate_grade(gear)
        return Stat.all_stat_multiplier(self.grade)


class BossDamageMultiplierBonus(Bonus):
    def calculate_improvement(self, gear: Gear) -> Stat:
        self.validate_grade(gear)
        return Stat(boss_damage_multiplier=self.grade * 2)


class DamageMultiplierBonus(Bonus):
    def calculate_improvement(self, gear: Gear) -> Stat:
        self.validate_grade(gear)
        return Stat(damage_multiplier=self.grade)


class ResourcePointBonus(Bonus):
    stat_type: Literal["MHP", "MMP"]

    def calculate_improvement(self, gear: Gear) -> Stat:
        self.validate_grade(gear)
        return Stat.parse_obj({self.stat_type: gear.req_level // 10 * 30 * self.grade})


class AttackTypeBonus(Bonus):
    attack_type: AttackType

    def calculate_improvement(self, gear: Gear) -> Stat:
        self.validate_grade(gear)
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
