import pytest
from loguru import logger

from simaple.core.base import Stat
from simaple.gear.gear_repository import GearRepository
from simaple.gear.improvements.starforce import Starforce

# 1005197 - 150 / 1102794 - 160 / 1102942 - 200
TEST_CASES_ARMOR = [
    (1005197, 1, Stat(INT=2, LUK=2, MHP=5)),
    (1005200, 3, Stat(STR=2, DEX=2, MHP=5)),
    (1005199, 6, Stat(DEX=3, LUK=3, MHP=15)),
    (1005197, 18, Stat(INT=11, LUK=11, attack_power=11, magic_attack=11)),
    (1102794, 1, Stat(INT=2, LUK=2, MHP=5)),
    (1102794, 3, Stat(INT=2, LUK=2, MHP=5)),
    (1102794, 6, Stat(INT=3, LUK=3, MHP=15)),
    (
        1102794,
        18,
        Stat(INT=13, LUK=13, STR=13, DEX=13, attack_power=12, magic_attack=12),
    ),
    (1102942, 1, Stat(DEX=2, STR=2, MHP=5)),
    (1102942, 3, Stat(DEX=2, STR=2, MHP=5)),
    (1102942, 5, Stat(DEX=2, STR=2, MHP=10)),
    (
        1102942,
        18,
        Stat(DEX=15, STR=15, INT=15, LUK=15, attack_power=14, magic_attack=14),
    ),
]


@pytest.mark.parametrize("gear_id, current_star, target", TEST_CASES_ARMOR)
def test_get_single_starforce_improvement(gear_id, current_star, target):
    repository = GearRepository()

    gear = repository.get_by_id(gear_id)
    starforce = Starforce(star=25)  # For single-starforce test, set as maximum

    starforce_stat = starforce.get_single_starforce_improvement(
        gear, current_star, Stat()
    )
    logger.info(starforce_stat)

    assert starforce_stat == target


TEST_CASES_FULL = [
    (1005303, 3, Stat(), Stat(INT=6, LUK=6, MHP=15)),  # 150, 법사모자
    (1005303, 7, Stat(), Stat(INT=16, LUK=16, MHP=65)),
    (
        1005303,
        18,
        Stat(attack_power=1),
        Stat(attack_power=30, magic_attack=30, INT=73, LUK=73, MHP=255),
    ),
    (
        1005303,
        22,
        Stat(),
        Stat(attack_power=85, magic_attack=85, INT=117, LUK=117, MHP=255),
    ),
    (1082640, 3, Stat(), Stat(STR=6, DEX=6)),  # 160, 해적장갑
    (1082640, 7, Stat(), Stat(STR=16, DEX=16, attack_power=2)),
    (
        1082640,
        18,
        Stat(attack_power=1),
        Stat(attack_power=40, magic_attack=33, STR=79, DEX=79),
    ),
    (1082640, 22, Stat(), Stat(attack_power=99, magic_attack=92, STR=131, DEX=131)),
    (1073160, 3, Stat(), Stat(DEX=6, STR=6)),  # 200, 궁수신발
    (1073160, 7, Stat(), Stat(DEX=16, STR=16)),
    (
        1073160,
        18,
        Stat(attack_power=1),
        Stat(attack_power=39, magic_attack=39, DEX=85, STR=85),
    ),
    (1073160, 22, Stat(), Stat(attack_power=106, magic_attack=106, DEX=145, STR=145)),
    (
        1212063,
        1,
        Stat(magic_attack=81),
        Stat(attack_power=3, magic_attack=6, INT=2, LUK=2, MHP=5, MMP=5),
    ),  # 150, 샤이닝로드
    (
        1212063,
        5,
        Stat(magic_attack=81),
        Stat(attack_power=15, magic_attack=32, INT=10, LUK=10, MHP=35, MMP=35),
    ),
    (
        1212063,
        18,
        Stat(magic_attack=81),
        Stat(attack_power=75, magic_attack=132, INT=73, LUK=73, MHP=255, MMP=255),
    ),
    (
        1212063,
        22,
        Stat(magic_attack=81),
        Stat(attack_power=121, magic_attack=178, INT=117, LUK=117, MHP=255, MMP=255),
    ),
    (
        1362147,
        1,
        Stat(attack_power=81),
        Stat(attack_power=5, DEX=2, LUK=2, MHP=5, MMP=5),
    ),  # 150, 케인
    (
        1362147,
        5,
        Stat(attack_power=81),
        Stat(attack_power=29, DEX=10, LUK=10, MHP=35, MMP=35),
    ),
    (
        1362147,
        18,
        Stat(attack_power=81),
        Stat(attack_power=120, DEX=73, LUK=73, MHP=255, MMP=255),
    ),
    (
        1362147,
        22,
        Stat(attack_power=81),
        Stat(attack_power=166, DEX=117, LUK=117, MHP=255, MMP=255),
    ),
    (
        1472261,
        1,
        Stat(attack_power=81),
        Stat(attack_power=4, DEX=2, LUK=2, MHP=5, MMP=5),
    ),  # 160, 아대
    (
        1472261,
        5,
        Stat(attack_power=81),
        Stat(attack_power=21, DEX=10, LUK=10, MHP=35, MMP=35),
    ),
    (
        1472261,
        18,
        Stat(attack_power=81),
        Stat(attack_power=100, DEX=79, LUK=79, MHP=255, MMP=255),
    ),
    (
        1472261,
        22,
        Stat(attack_power=81),
        Stat(attack_power=150, DEX=131, LUK=131, MHP=255, MMP=255),
    ),
    (
        1462243,
        1,
        Stat(attack_power=81),
        Stat(attack_power=8, DEX=2, STR=2, MHP=5, MMP=5),
    ),  # 200, 석궁
    (
        1462243,
        5,
        Stat(attack_power=81),
        Stat(attack_power=40, DEX=10, STR=10, MHP=35, MMP=35),
    ),
    (
        1462243,
        18,
        Stat(attack_power=81),
        Stat(attack_power=174, DEX=85, STR=85, MHP=255, MMP=255),
    ),
    (
        1462243,
        22,
        Stat(attack_power=81),
        Stat(attack_power=236, DEX=145, STR=145, MHP=255, MMP=255),
    ),
]


@pytest.mark.parametrize("gear_id, star, scroll, target", TEST_CASES_FULL)
def test_get_starforce_improvement(gear_id, star, scroll, target):
    repository = GearRepository()

    gear = repository.get_by_id(gear_id)
    gear.stat += scroll
    starforce = Starforce(star=star)

    starforce_stat = starforce.calculate_improvement(gear)
    logger.info(starforce_stat)

    assert starforce_stat == target
