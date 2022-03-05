import pytest
from loguru import logger

from simaple.core.base import Stat
from simaple.gear.gear_repository import GearRepository
from simaple.gear.improvements.starforce import AmazingEnhancement

TEST_CASES_ARMOR = [
    (1113149, 1, Stat(STR=9, INT=9, DEX=9, LUK=9)),
    (1113149, 3, Stat(STR=31, INT=31, DEX=31, LUK=31)),
    (1113149, 6, Stat(STR=65, INT=65, DEX=65, LUK=65, attack_power=5, magic_attack=5)),
    (
        1113149,
        8,
        Stat(STR=65, INT=65, DEX=65, LUK=65, attack_power=18, magic_attack=18),
    ),
    (1122076, 1, Stat(STR=12, INT=12, DEX=12, LUK=12)),
    (1122076, 3, Stat(STR=40, INT=40, DEX=40, LUK=40)),
    (1122076, 6, Stat(STR=80, INT=80, DEX=80, LUK=80, attack_power=6, magic_attack=6)),
    (
        1122076,
        8,
        Stat(STR=80, INT=80, DEX=80, LUK=80, attack_power=21, magic_attack=21),
    ),
    (1005197, 1, Stat(INT=19, LUK=19)),
    (1005197, 3, Stat(INT=61, LUK=61)),
    (1005197, 6, Stat(INT=115, LUK=115, magic_attack=9)),
    (1005197, 12, Stat(INT=115, LUK=115, magic_attack=85)),
]


@pytest.mark.parametrize("gear_id, star, target", TEST_CASES_ARMOR)
def test_get_starforce_improvement(gear_id, star, target):
    repository = GearRepository()

    gear = repository.get_by_id(gear_id)
    amazing_enhancement = AmazingEnhancement(star=star)

    improvement_stat = amazing_enhancement.calculate_improvement(gear)
    logger.info(improvement_stat)

    assert improvement_stat == target
