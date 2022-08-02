from __future__ import annotations

from typing import Iterable, Optional

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


class FastBonusSdilFactory(pydantic.BaseModel):
    lookup: dict[BonusType, list[Optional[SDIL]]]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def build(cls, gear: Gear):
        bf = BonusFactory()
        lookup = {}
        grade_range = [3, 4, 5, 6, 7] if gear.boss_reward else [1, 2, 3, 4, 5, 6, 7]
        for t in _stat_types:
            sdil_list: list[list[int]] = []
            lookup[t] = sdil_list
            for g in range(8):
                if g not in grade_range:
                    sdil_list.append(None)
                else:
                    stat = bf.create(t, g).calculate_improvement(gear)
                    sdil_list.append(SDIL.from_stat(stat))

        return FastBonusSdilFactory(
            lookup=lookup,
        )

    def get_sdil(self, bonus_type: BonusType, grade: int) -> list[int]:
        return self.lookup[bonus_type][grade]


class CachedBonusTypeProvider:
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
    grades: list[int]
    bonus_factory: BonusFactory
    fast_bonus_factory: Optional[FastBonusSdilFactory] = None
    bonus_type_provider: CachedBonusTypeProvider = pydantic.Field(
        default_factory=CachedBonusTypeProvider
    )
    total_bonus_count: int

    class Config:
        arbitrary_types_allowed = True

    def compute(self, stat: Stat) -> list[Bonus]:
        reference_sdil = SDIL.from_stat(stat)

        searched_bonus = self._search_bonus(
            reference_sdil, self.total_bonus_count, forbidden_bonus_types=[]
        )
        if searched_bonus is None:
            raise ValueError(
                "gear stat has invalid bonus value or has too many bonus values"
            )

        return searched_bonus

    def _search_bonus(
        self, remaining_sdil: SDIL, left: int, forbidden_bonus_types: list
    ) -> Optional[list[Bonus]]:
        if remaining_sdil.is_zero():
            return []
        if left <= 0 or remaining_sdil.has_negative():
            return None

        for bonus_type in self.bonus_type_provider.get_types(remaining_sdil):
            if bonus_type in forbidden_bonus_types:
                continue

            appended_forbidden_bonus_types = forbidden_bonus_types + [bonus_type]

            for grade in self.grades:
                bonus_sdil = self.fast_bonus_factory.get_sdil(bonus_type, grade)
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
    # private fields
    grades: list[int] = []
    bonus_factory = BonusFactory()
    bonus_types: list = []

    class Config:
        arbitrary_types_allowed = True

    def compute(self, stat: Stat, gear: Gear) -> list[Bonus]:
        """
        * 실행 시 마다 결과가 달라질 수 있음
        * _get_bonus_types() 함수가 항상 동일한 순서로 반환하도록 수정하면 일정한 결과를 반환함
        :param stat: bonus stat
        :param gear:
        :return:
        """
        # 환생의 불꽃 추가옵션 부여 확률이 높은 등급부터 계산
        self.grades = [5, 4, 6, 3, 7] if gear.boss_reward else [5, 4, 6, 3, 2, 1, 7]
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
                for grade in self.grades:
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

        stat_bonus_calculator = StatBonusCalculator(
            grades=self.grades,
            bonus_factory=self.bonus_factory,
            fast_bonus_factory=FastBonusSdilFactory.build(gear),
            bonus_type_provider=CachedBonusTypeProvider(),
            total_bonus_count=bonus_count_left,
        )

        bonus_list += stat_bonus_calculator.compute(stat)

        return bonus_list
