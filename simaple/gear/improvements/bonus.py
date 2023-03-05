import math
from typing import Annotated, Literal, Optional, Tuple

from pydantic import conint

from simaple.core import Stat
from simaple.core.base import AttackType, BaseStatType
from simaple.gear.gear import GearMeta
from simaple.gear.gear_type import GearType
from simaple.gear.improvements.base import GearImprovement


class Bonus(GearImprovement):
    type: Literal["bonus"] = "bonus"
    grade: Annotated[int, conint(ge=1, le=7)]

    def validate_grade(self, meta: GearMeta):
        if meta.boss_reward and self.grade < 3:
            raise ValueError("boss reward cannot assigned less than 3")


class SingleStatBonus(Bonus):
    stat_type: BaseStatType

    @staticmethod
    def calculate_basis(req_level: int) -> int:
        return req_level // 20 + 1

    def calculate_improvement(self, meta: GearMeta, _: Optional[Stat] = None) -> Stat:
        self.validate_grade(meta)
        basis = self.calculate_basis(meta.req_level)
        increment = basis * self.grade

        return Stat.parse_obj({self.stat_type.value: increment})


class DualStatBonus(Bonus):
    stat_type_pair: Tuple[BaseStatType, BaseStatType]

    @staticmethod
    def calculate_basis(req_level: int) -> int:
        return req_level // 40 + 1

    def calculate_improvement(self, meta: GearMeta, _: Optional[Stat] = None) -> Stat:
        self.validate_grade(meta)
        first_type, second_type = self.stat_type_pair
        basis = self.calculate_basis(meta.req_level)
        increment = basis * self.grade

        return Stat.parse_obj(
            {first_type.value: increment, second_type.value: increment}
        )


class AllstatBonus(Bonus):
    def calculate_improvement(self, meta: GearMeta, _: Optional[Stat] = None) -> Stat:
        self.validate_grade(meta)
        return Stat.all_stat_multiplier(self.grade)


class BossDamageMultiplierBonus(Bonus):
    def calculate_improvement(self, meta: GearMeta, _: Optional[Stat] = None) -> Stat:
        self.validate_grade(meta)
        return Stat(boss_damage_multiplier=self.grade * 2)


class DamageMultiplierBonus(Bonus):
    def calculate_improvement(self, meta: GearMeta, _: Optional[Stat] = None) -> Stat:
        self.validate_grade(meta)
        return Stat(damage_multiplier=self.grade)


class ResourcePointBonus(Bonus):
    stat_type: Literal["MHP", "MMP"]

    def calculate_improvement(self, meta: GearMeta, _: Optional[Stat] = None) -> Stat:
        self.validate_grade(meta)
        return Stat.parse_obj({self.stat_type: meta.req_level // 10 * 30 * self.grade})


class AttackTypeBonus(Bonus):
    attack_type: AttackType

    def calculate_improvement(self, meta: GearMeta, _: Optional[Stat] = None) -> Stat:
        self.validate_grade(meta)

        if meta.type.is_weapon():
            grade_multiplier = (
                [0, 0, 1, 1.4666, 2.0166, 2.663, 3.4166]
                if meta.boss_reward
                else [1, 2.222, 3.63, 5.325, 7.32, 8.777, 10.25]
            )

            basis = (
                meta.base_stat.attack_power
                if meta.base_stat.attack_power > meta.base_stat.magic_attack
                else meta.base_stat.magic_attack
            )

            if meta.type in (GearType.sword_zb, GearType.sword_zl):
                if meta.type == GearType.sword_zl:
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
                        print("Not implemented weapon:\n" + str(meta))
                level_multiplier = (
                    6
                    if meta.req_level > 180
                    else (
                        5
                        if meta.req_level > 160
                        else (4 if meta.req_level > 110 else 3)
                    )
                )
            else:
                if meta.boss_reward:
                    level_multiplier = (
                        18
                        if meta.req_level > 160
                        else (
                            15
                            if meta.req_level > 150
                            else (12 if meta.req_level > 110 else 9)
                        )
                    )
                else:
                    level_multiplier = 4 if meta.req_level > 110 else 3

            value = math.ceil(
                basis * grade_multiplier[self.grade - 1] * level_multiplier / 100
            )
        else:
            value = self.grade

        return Stat.parse_obj({self.attack_type.value: value})


def bonus_key_func(bonus: Bonus):
    # STR_DEX: 2, STR_INT: 3, STR_LUK: 4, DEX_INT: 5, DEX_LUK: 6, INT_LUK: 7
    stat_index = {
        BaseStatType.STR: 0,
        BaseStatType.DEX: 2,
        BaseStatType.INT: 3,
        BaseStatType.LUK: 4,
    }
    resource_point_index = {"MHP": 0, "MMP": 1}
    attack_type_index = {AttackType.attack_power: 0, AttackType.magic_attack: 1}
    if isinstance(bonus, SingleStatBonus):
        return stat_index[bonus.stat_type] * 100 + bonus.grade
    if isinstance(bonus, DualStatBonus):
        return (
            (10**3)
            + (
                stat_index[bonus.stat_type_pair[0]]
                + stat_index[bonus.stat_type_pair[1]]
            )
            * 100
            + bonus.grade
        )
    if isinstance(bonus, ResourcePointBonus):
        return (10**4) + resource_point_index[bonus.stat_type] * 100 + bonus.grade
    if isinstance(bonus, AttackTypeBonus):
        return (10**5) + attack_type_index[bonus.attack_type] * 100 + bonus.grade
    if isinstance(bonus, BossDamageMultiplierBonus):
        return (10**6) + bonus.grade
    if isinstance(bonus, DamageMultiplierBonus):
        return (10**7) + bonus.grade
    if isinstance(bonus, AllstatBonus):
        return (10**8) + bonus.grade
    return 10**9
