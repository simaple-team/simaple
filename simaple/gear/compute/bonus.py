import time
from typing import List, Dict, Tuple, Iterable
from itertools import product

from simaple.core import Stat
from simaple.gear.bonus_factory import BonusFactory, BonusType
from simaple.gear.compute.base import GearImprovementCalculator
from simaple.gear.gear import Gear
from simaple.gear.gear_repository import GearRepository
from simaple.gear.improvements.bonus import Bonus

_MAX_BONUS = 4
_stat_types = [
    BonusType.STR, BonusType.DEX, BonusType.INT, BonusType.LUK,
    BonusType.STR_DEX, BonusType.STR_INT, BonusType.STR_LUK,
    BonusType.DEX_INT, BonusType.DEX_LUK, BonusType.INT_LUK
]


class FastBonusSdilFactory:
    index_offset: int
    lookup: Dict[BonusType, List[List[int]]]

    def init(self, gear: Gear):
        bf = BonusFactory()
        lookup = dict()
        grade_range = [3, 4, 5, 6, 7] if gear.boss_reward else [1, 2, 3, 4, 5, 6, 7]
        for t in _stat_types:
            sdil_list: List[List[int]] = []
            lookup[t] = sdil_list
            for g in grade_range:
                stat = bf.create(t, g).calculate_improvement(gear)
                sdil_list.append([stat.STR, stat.DEX, stat.INT, stat.LUK])
        self.lookup = lookup
        self.index_offset = 3 if gear.boss_reward else 1

    def get_sdil(self, bonus_type: BonusType, grade: int) -> List[int]:
        return self.lookup[bonus_type][grade - self.index_offset]


class BonusTypeCalculator:
    lookup: List[Iterable[BonusType]]

    def __init__(self):
        self.lookup = []
        for i in range(16):
            self.lookup.append(self._get_bonus_types(i))

    def _get_bonus_types(self, i: int) -> Iterable[BonusType]:
        bonus_types = set()
        if i & 1 << 0:
            bonus_types.update((BonusType.STR, BonusType.STR_DEX, BonusType.STR_INT, BonusType.STR_LUK))
        if i & 1 << 1:
            bonus_types.update((BonusType.DEX, BonusType.STR_DEX, BonusType.DEX_INT, BonusType.DEX_LUK))
        if i & 1 << 2:
            bonus_types.update((BonusType.INT, BonusType.STR_INT, BonusType.DEX_INT, BonusType.INT_LUK))
        if i & 1 << 3:
            bonus_types.update((BonusType.LUK, BonusType.STR_LUK, BonusType.DEX_LUK, BonusType.INT_LUK))
        return sorted(list(bonus_types), key=lambda x: x.value)

    def get_types(self, sdil: List[float]) -> Iterable[BonusType]:
        return self.lookup[
            (1 << 0 if sdil[0] > 0 else 0) + (1 << 1 if sdil[1] else 0) + (1 << 2 if sdil[2] else 0) + (1 << 3 if sdil[3] else 0)]


class BonusCalculator(GearImprovementCalculator):
    # private fields
    grades: List[int] = []
    bonus_factory = BonusFactory()
    fast_bonus_factory = FastBonusSdilFactory()
    fast_bonus_type_factory = BonusTypeCalculator()
    sdil_bonus_list: List[Tuple[BonusType, int]] = []

    class Config:
        arbitrary_types_allowed = True

    def compute(self, stat: Stat, gear: Gear) -> List[Bonus]:
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

        if stat.MHP > 0:
            error = True
            for grade in self.grades:
                bonus = self.bonus_factory.create(BonusType.MHP, grade)
                if bonus.calculate_improvement(gear).MHP == stat.MHP:
                    bonus_list.append(bonus)
                    bonus_count_left -= 1
                    error = False
                    break
            if error:
                raise ValueError("gear stat has invalid bonus MHP value")
        if stat.MMP > 0:
            error = True
            for grade in self.grades:
                bonus = self.bonus_factory.create(BonusType.MMP, grade)
                if bonus.calculate_improvement(gear).MMP == stat.MMP:
                    bonus_list.append(bonus)
                    bonus_count_left -= 1
                    error = False
                    break
            if error:
                raise ValueError("gear stat has invalid bonus MMP value")
        if stat.attack_power > 0:
            error = True
            for grade in self.grades:
                bonus = self.bonus_factory.create(BonusType.attack_power, grade)
                if bonus.calculate_improvement(gear).attack_power == stat.attack_power:
                    bonus_list.append(bonus)
                    bonus_count_left -= 1
                    error = False
                    break
            if error:
                raise ValueError("gear stat has invalid bonus attack_power value")
        if stat.magic_attack > 0:
            error = True
            for grade in self.grades:
                bonus = self.bonus_factory.create(BonusType.magic_attack, grade)
                if bonus.calculate_improvement(gear).magic_attack == stat.magic_attack:
                    bonus_list.append(bonus)
                    bonus_count_left -= 1
                    error = False
                    break
            if error:
                raise ValueError("gear stat has invalid bonus magic_attack value")
        if stat.boss_damage_multiplier > 0:
            error = True
            for grade in self.grades:
                bonus = self.bonus_factory.create(BonusType.boss_damage_multiplier, grade)
                if bonus.calculate_improvement(gear).boss_damage_multiplier == stat.boss_damage_multiplier:
                    bonus_list.append(bonus)
                    bonus_count_left -= 1
                    error = False
                    break
            if error:
                raise ValueError("gear stat has invalid bonus boss_damage_multiplier value")
        if stat.damage_multiplier > 0:
            error = True
            for grade in self.grades:
                bonus = self.bonus_factory.create(BonusType.damage_multiplier, grade)
                if bonus.calculate_improvement(gear).damage_multiplier == stat.damage_multiplier:
                    bonus_list.append(bonus)
                    bonus_count_left -= 1
                    error = False
                    break
            if error:
                raise ValueError("gear stat has invalid bonus damage_multiplier value")
        if stat.STR_multiplier > 0: # 올스탯 추옵을 나타내는 부분이 없어서 힘%로 대체
            error = True
            for grade in self.grades:
                bonus = self.bonus_factory.create(BonusType.all_stat_multiplier, grade)
                if bonus.calculate_improvement(gear).STR_multiplier == stat.STR_multiplier:
                    bonus_list.append(bonus)
                    bonus_count_left -= 1
                    error = False
                    break
            if error:
                raise ValueError("gear stat has invalid bonus STR_multiplier(all_stat) value")

        if bonus_count_left < 0:
            raise ValueError("gear stat has too many bonus values")

        self.fast_bonus_factory.init(gear)
        self.sdil_bonus_list = []
        sdil = [stat.STR, stat.DEX, stat.INT, stat.LUK]
        if not self._search_bonus(sdil, bonus_count_left, gear):
            raise ValueError("gear stat has invalid bonus value or has too many bonus values")

        for a in self.sdil_bonus_list:
            bonus_type, grade = a
            bonus_list.append(self.bonus_factory.create(bonus_type, grade))

        return bonus_list

    def _search_bonus(self, sdil: List[float], left: int, gear: Gear) -> bool:
        if self._is_zero(sdil):
            return True
        if left <= 0:
            return False
        if self._has_negative(sdil):
            return False
        for bonus_type in self.fast_bonus_type_factory.get_types(sdil):
            for grade in self.grades:
                bonus_sdil = self.fast_bonus_factory.get_sdil(bonus_type, grade)
                sdil_diff = self._sub_sdil(sdil, bonus_sdil)
                if self._search_bonus(sdil_diff, left - 1, gear):
                    self.sdil_bonus_list.append((bonus_type, grade))
                    return True
        return False

    def _to_sdil(self, stat: Stat) -> List[float]:
        return [stat.STR, stat.DEX, stat.INT, stat.LUK]

    def _sub_sdil(self, sdil1: List[float], sdil2: List[float]) -> List[float]:
        return [
            sdil1[0] - sdil2[0],
            sdil1[1] - sdil2[1],
            sdil1[2] - sdil2[2],
            sdil1[3] - sdil2[3],
        ]

    def _is_zero(self, sdil: List[float]) -> bool:
        return sdil[0] == 0 and sdil[1] == 0 and sdil[2] == 0 and sdil[3] == 0

    def _has_negative(self, sdil: List[float]) -> bool:
        return sdil[0] < 0 or sdil[1] < 0 or sdil[2] < 0 or sdil[3] < 0
