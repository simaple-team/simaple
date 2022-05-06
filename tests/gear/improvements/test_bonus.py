import pytest
from loguru import logger

from simaple.core import Stat
from simaple.core.base import AttackType, BaseStatType
from simaple.gear.gear_repository import GearRepository
from simaple.gear.improvements.bonus import (
    AllstatBonus,
    AttackTypeBonus,
    BossDamageMultiplierBonus,
    DamageMultiplierBonus,
    DualStatBonus,
    SingleStatBonus,
)

TEST_CASES_ARMOR = [
    (1005197, SingleStatBonus(stat_type=BaseStatType.DEX, grade=3), Stat(DEX=24)),
    (1005197, SingleStatBonus(stat_type=BaseStatType.DEX, grade=7), Stat(DEX=56)),
    (
        1005197,
        DualStatBonus(stat_type_pair=(BaseStatType.STR, BaseStatType.DEX), grade=3),
        Stat(DEX=12, STR=12),
    ),
    (1102794, SingleStatBonus(stat_type=BaseStatType.DEX, grade=3), Stat(DEX=27)),
    (1102794, SingleStatBonus(stat_type=BaseStatType.DEX, grade=7), Stat(DEX=63)),
    (
        1102794,
        DualStatBonus(stat_type_pair=(BaseStatType.STR, BaseStatType.DEX), grade=3),
        Stat(DEX=15, STR=15),
    ),
    (1102942, SingleStatBonus(stat_type=BaseStatType.DEX, grade=3), Stat(DEX=33)),
    (1102942, SingleStatBonus(stat_type=BaseStatType.DEX, grade=7), Stat(DEX=77)),
    (
        1102942,
        DualStatBonus(stat_type_pair=(BaseStatType.STR, BaseStatType.DEX), grade=3),
        Stat(DEX=18, STR=18),
    ),
    (
        1005197,
        AttackTypeBonus(attack_type=AttackType.magic_attack, grade=3),
        Stat(magic_attack=3),
    ),
    (
        1005197,
        AttackTypeBonus(attack_type=AttackType.attack_power, grade=5),
        Stat(attack_power=5),
    ),
    (1005197, AllstatBonus(grade=6), Stat.all_stat_multiplier(6)),
]

TEST_CASES_WEAPON = [
    (
        1212063,
        AttackTypeBonus(attack_type=AttackType.magic_attack, grade=5),
        Stat(magic_attack=49),
    ),
    (
        1212063,
        AttackTypeBonus(attack_type=AttackType.magic_attack, grade=7),
        Stat(magic_attack=83),
    ),
    (
        1212063,
        AttackTypeBonus(attack_type=AttackType.attack_power, grade=5),
        Stat(attack_power=49),
    ),
    (
        1212063,
        AttackTypeBonus(attack_type=AttackType.attack_power, grade=7),
        Stat(attack_power=83),
    ),
    (
        1572007,
        AttackTypeBonus(attack_type=AttackType.attack_power, grade=1),
        Stat(attack_power=9),
    ),
    (
        1572007,
        AttackTypeBonus(attack_type=AttackType.magic_attack, grade=3),
        Stat(magic_attack=32),
    ),
    (
        1572007,
        AttackTypeBonus(attack_type=AttackType.attack_power, grade=5),
        Stat(attack_power=64),
    ),
    (
        1442274,
        AttackTypeBonus(attack_type=AttackType.attack_power, grade=3),
        Stat(attack_power=48),
    ),
    (
        1442274,
        AttackTypeBonus(attack_type=AttackType.magic_attack, grade=5),
        Stat(magic_attack=96),
    ),
    (
        1442274,
        AttackTypeBonus(attack_type=AttackType.attack_power, grade=7),
        Stat(attack_power=163),
    ),
    (1442274, BossDamageMultiplierBonus(grade=7), Stat(boss_damage_multiplier=14)),
    (1442274, DamageMultiplierBonus(grade=7), Stat(damage_multiplier=7)),
]


@pytest.mark.parametrize("gear_id, bonus, target", TEST_CASES_ARMOR + TEST_CASES_WEAPON)
def test_armor_bonus(gear_id, bonus, target):
    repository = GearRepository()

    gear = repository.get_by_id(gear_id)
    bonus_stat = bonus.calculate_improvement(gear)
    logger.info(gear)

    assert bonus_stat == target
