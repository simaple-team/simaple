import time

import pytest

from simaple.core import Stat
from simaple.core.base import AttackType, BaseStatType
from simaple.gear.compute.bonus import BonusCalculator
from simaple.gear.gear_repository import GearRepository
from simaple.gear.improvements import bonus


@pytest.mark.parametrize(
    "gear_name, stat, expected",
    [
        (
            "앱솔랩스 메이지케이프",
            Stat(STR=54 + 20 + 20 + 20, INT=20, DEX=20, LUK=20),
            [
                bonus.DualStatBonus(
                    grade=4,
                    stat_type_pair=(
                        BaseStatType.STR,
                        BaseStatType.LUK,
                    ),
                ),
                bonus.DualStatBonus(
                    grade=4,
                    stat_type_pair=(
                        BaseStatType.STR,
                        BaseStatType.INT,
                    ),
                ),
                bonus.DualStatBonus(
                    grade=4,
                    stat_type_pair=(
                        BaseStatType.STR,
                        BaseStatType.DEX,
                    ),
                ),
                bonus.SingleStatBonus(grade=6, stat_type=BaseStatType.STR),
            ],
        )
    ],
)
def test_bonus(gear_name, stat, expected):
    start = time.time()
    gear_repository = GearRepository()
    calculator = BonusCalculator()

    gear = gear_repository.get_by_name(gear_name)

    for _ in range(100):
        result = calculator.compute(stat, gear)

    end = time.time()

    assert expected == result
    assert (end - start) / 100 < 0.1  # less-than-100ms

    print((end - start) / 100)
