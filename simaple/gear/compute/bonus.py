from __future__ import annotations

from itertools import combinations, product
from typing import Iterable, Optional, Generator

import pydantic

from simaple.core import Stat, StatProps
from simaple.gear.bonus_factory import BonusFactory, BonusType
from simaple.gear.compute.base import GearImprovementCalculator
from simaple.gear.gear import Gear
from simaple.gear.improvements.bonus import Bonus

_MAX_BONUS = 4
_stat_types = [
    BonusType.STR,
    BonusType.DEX,
    BonusType.INT,
    BonusType.LUK,
    BonusType.STR_DEX,
    BonusType.STR_INT,
    BonusType.STR_LUK,
    BonusType.DEX_INT,
    BonusType.DEX_LUK,
    BonusType.INT_LUK,
]


class SDIL:
    def __init__(self, value: tuple[int, int, int, int]):
        self.value = value

    @classmethod
    def from_stat(cls, stat: Stat):
        return cls(value=(stat.STR, stat.DEX, stat.INT, stat.LUK))

    def __sub__(self, arg: SDIL):
        return SDIL(
            value=(
                self.value[0] - arg.value[0],
                self.value[1] - arg.value[1],
                self.value[2] - arg.value[2],
                self.value[3] - arg.value[3],
            )
        )

    def is_zero(self):
        return (
            self.value[0] == 0
            and self.value[1] == 0
            and self.value[2] == 0
            and self.value[3] == 0
        )

    def has_negative(self) -> bool:
        return (
            self.value[0] < 0
            or self.value[1] < 0
            or self.value[2] < 0
            or self.value[3] < 0
        )

    def get_index(self):
        idx = 0
        for power in range(3):
            idx += 1 << power if self.value[power] else 0

        return idx


class SDILTableBuilder(pydantic.BaseModel):
    def build(self, gear: Gear):
        bf = BonusFactory()
        cache = {}
        grade_range = [3, 4, 5, 6, 7] if gear.boss_reward else [1, 2, 3, 4, 5, 6, 7]
        for t in _stat_types:
            sdil_list = []
            cache[t] = sdil_list
            for g in range(8):
                if g not in grade_range:
                    sdil_list.append(None)
                else:
                    stat = bf.create(t, g).calculate_improvement(gear)
                    sdil_list.append(SDIL.from_stat(stat))

        return cache


class CachedBonusTypeTable:
    lookup: list[Iterable[BonusType]]

    def __init__(self):
        self.lookup = []
        for i in range(16):
            self.lookup.append(self._get_bonus_types(i))

    def _get_bonus_types(self, i: int) -> Iterable[BonusType]:
        bonus_types = set()
        if i & 1 << 0:
            bonus_types.update(
                (BonusType.STR, BonusType.STR_DEX, BonusType.STR_INT, BonusType.STR_LUK)
            )
        if i & 1 << 1:
            bonus_types.update(
                (BonusType.DEX, BonusType.STR_DEX, BonusType.DEX_INT, BonusType.DEX_LUK)
            )
        if i & 1 << 2:
            bonus_types.update(
                (BonusType.INT, BonusType.STR_INT, BonusType.DEX_INT, BonusType.INT_LUK)
            )
        if i & 1 << 3:
            bonus_types.update(
                (BonusType.LUK, BonusType.STR_LUK, BonusType.DEX_LUK, BonusType.INT_LUK)
            )
        return sorted(list(bonus_types), key=lambda x: x.value)

    def get_types(self, sdil: SDIL) -> Iterable[BonusType]:
        return self.lookup[sdil.get_index()]


class StatBonusCalculator(pydantic.BaseModel):
    bonus_factory: BonusFactory = pydantic.Field(default_factory=BonusFactory)
    sdil_table_builder: SDILTableBuilder = pydantic.Field(
        default_factory=SDILTableBuilder
    )
    bonus_type_table: CachedBonusTypeTable = pydantic.Field(
        default_factory=CachedBonusTypeTable
    )

    _sdil_table: dict[BonusType, list[Optional[SDIL]]]
    _grades: list[int]

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True

    def compute(self, stat: Stat, gear: Gear, bonus_count_left: int) -> list[Bonus]:
        self._sdil_table = self.sdil_table_builder.build(gear)
        self._grades = [5, 4, 6, 3, 7] if gear.boss_reward else [5, 4, 6, 3, 2, 1, 7]

        target_sdil = SDIL.from_stat(stat)

        bonus_list = self._search_bonus_with_grade_list(
            target_sdil, gear, bonus_count_left
        )
        if bonus_list is None:
            raise ValueError(
                "gear stat has invalid bonus value or has too many bonus values"
            )

        return bonus_list

    def _grade_combinations(
        self, value: int, left: int, single_stat_increment: int, dual_stat_increment: int
    ) -> Generator[tuple[int]]:
        for count in range(1, left + 1):
            for single_grade in self._grades:
                dual_value = value - single_grade * single_stat_increment
                if dual_value == 0:
                    yield (single_grade,)
                if dual_value % dual_stat_increment == 0:
                    dual_grade_sum = dual_value // dual_stat_increment
                    for dual_grade_tuple in product(self._grades, repeat=count - 1):
                        if sum(dual_grade_tuple) == dual_grade_sum:
                            yield (single_grade,) + dual_grade_tuple

    def _search_bonus_with_grade_list(
        self, target_sdil: SDIL, gear: Gear, left: int
    ) -> Optional[list[Bonus]]:
        _dual_bonus_types = {
            BonusType.STR: (BonusType.STR_DEX, BonusType.STR_INT, BonusType.STR_LUK),
            BonusType.DEX: (BonusType.STR_DEX, BonusType.DEX_INT, BonusType.DEX_LUK),
            BonusType.INT: (BonusType.STR_INT, BonusType.DEX_INT, BonusType.INT_LUK),
            BonusType.LUK: (BonusType.STR_LUK, BonusType.DEX_LUK, BonusType.INT_LUK),
        }

        if target_sdil.is_zero():
            return []

        single_stat_increment = gear.req_level // 20 + 1  # Calculate manually
        dual_stat_increment = gear.req_level // 40 + 1
        _max_index = target_sdil.value.index(max(target_sdil.value))
        max_value = target_sdil.value[_max_index]
        max_type = [BonusType.STR, BonusType.DEX, BonusType.INT, BonusType.LUK][_max_index]

        for grade_list in self._grade_combinations(
            max_value, left, single_stat_increment, dual_stat_increment
        ):
            left_count = left - len(grade_list)
            max_type_grade = grade_list[0]
            remaining_sdil = target_sdil - self._sdil_table[max_type][max_type_grade]
            forbidden_types = [max_type]

            if len(grade_list[1:]) == 0:
                return self._search_bonus(remaining_sdil, left_count, forbidden_types) + [
                    self.bonus_factory.create(max_type, max_type_grade)
                ]
            else:
                for dual_type_tuple in combinations(
                    _dual_bonus_types[max_type], len(grade_list[1:])
                ):
                    dual_remaining_sdil = remaining_sdil
                    forbidden_types_dual = list(forbidden_types)
                    for dual_type, dual_grade in zip(dual_type_tuple, grade_list[1:]):
                        dual_remaining_sdil -= self._sdil_table[dual_type][dual_grade]
                        forbidden_types_dual += [dual_type]
                    result = self._search_bonus(
                        dual_remaining_sdil, left_count, forbidden_types_dual
                    )
                    if result is not None:
                        result.append(self.bonus_factory.create(max_type, max_type_grade))
                        for dual_type, dual_grade in zip(dual_type_tuple, grade_list[1:]):
                            result.append(self.bonus_factory.create(dual_type, dual_grade))
                        return result

        return None

    def _search_bonus(
        self, remaining_sdil: SDIL, left: int, forbidden_bonus_types: list
    ) -> Optional[list[Bonus]]:
        if remaining_sdil.is_zero():
            return []
        if left <= 0 or remaining_sdil.has_negative():
            return None

        for bonus_type in self.bonus_type_table.get_types(remaining_sdil):
            if bonus_type in forbidden_bonus_types:
                continue

            appended_forbidden_bonus_types = forbidden_bonus_types + [bonus_type]

            for grade in self._grades:
                bonus_sdil = self._sdil_table[bonus_type][grade]
                decreased_sdil = remaining_sdil - bonus_sdil

                bonus_candidate = self._search_bonus(
                    decreased_sdil, left - 1, appended_forbidden_bonus_types
                )
                if bonus_candidate is not None:
                    return bonus_candidate + [
                        self.bonus_factory.create(bonus_type, grade)
                    ]

        return None


class BonusCalculator(GearImprovementCalculator):
    bonus_factory: BonusFactory = pydantic.Field(default_factory=BonusFactory)
    stat_bonus_calculator: StatBonusCalculator = pydantic.Field(
        default_factory=StatBonusCalculator
    )

    class Config:
        arbitrary_types_allowed = True

    def compute(self, stat: Stat, gear: Gear) -> list[Bonus]:
        # 환생의 불꽃 추가옵션 부여 확률이 높은 등급부터 계산
        grades = [5, 4, 6, 3, 7] if gear.boss_reward else [5, 4, 6, 3, 2, 1, 7]
        bonus_count_left = _MAX_BONUS
        bonus_list = []

        single_properties = [
            (StatProps.MHP, BonusType.MHP),
            (StatProps.MMP, BonusType.MMP),
            (StatProps.attack_power, BonusType.attack_power),
            (StatProps.magic_attack, BonusType.magic_attack),
            (StatProps.boss_damage_multiplier, BonusType.boss_damage_multiplier),
            (StatProps.damage_multiplier, BonusType.damage_multiplier),
            (StatProps.STR_multiplier, BonusType.all_stat_multiplier),
        ]

        for single_property in single_properties:
            stat_type, bonus_type = single_property
            if stat.get(stat_type) > 0:
                error = True
                for grade in grades:
                    bonus = self.bonus_factory.create(bonus_type, grade)
                    if bonus.calculate_improvement(gear).get(stat_type) == stat.get(
                        stat_type
                    ):
                        bonus_list.append(bonus)
                        bonus_count_left -= 1
                        error = False
                        break
                if error:
                    raise ValueError(f"gear stat has invalid bonus at {bonus_type}")

        if bonus_count_left < 0:
            raise ValueError("gear stat has too many bonus values")

        bonus_list += self.stat_bonus_calculator.compute(stat, gear, bonus_count_left)

        return bonus_list
