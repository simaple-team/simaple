from simaple.gear.improvements.bonus import BonusType, Bonus
from simaple.gear.gear_repository import GearRepository
from simaple.core.base import Stat, Ability

import pytest
from loguru import logger

TEST_CASES_ARMOR = [
    (1005197, BonusType.DEX, 3, Stat(ability=Ability(DEX=24))),
    (1005197, BonusType.DEX, 7, Stat(ability=Ability(DEX=56))),
    (1005197, BonusType.STR_DEX, 3, Stat(ability=Ability(DEX=12, STR=12))),

    (1102794, BonusType.DEX, 3, Stat(ability=Ability(DEX=27))),
    (1102794, BonusType.DEX, 7, Stat(ability=Ability(DEX=63))),
    (1102794, BonusType.STR_DEX, 3, Stat(ability=Ability(DEX=15, STR=15))),

    (1102942, BonusType.DEX, 3, Stat(ability=Ability(DEX=33))),
    (1102942, BonusType.DEX, 7, Stat(ability=Ability(DEX=77))),
    (1102942, BonusType.STR_DEX, 3, Stat(ability=Ability(DEX=18, STR=18))),

    (1005197, BonusType.magic_attack, 3, Stat(magic_attack=3)),
    (1005197, BonusType.attack_power, 5, Stat(attack_power=5)),
    (1005197, BonusType.all_stat_multiplier, 6, Stat.all_stat_multiplier(6)),
]

TEST_CASES_WEAPON = [
    (1212063, BonusType.magic_attack, 5, Stat(magic_attack=49)),
    (1212063, BonusType.magic_attack, 7, Stat(magic_attack=83)),
    (1212063, BonusType.attack_power, 5, Stat(attack_power=49)),
    (1212063, BonusType.attack_power, 7, Stat(attack_power=83)),

    (1572007, BonusType.attack_power, 1, Stat(attack_power=9)),
    (1572007, BonusType.magic_attack, 3, Stat(magic_attack=32)),
    (1572007, BonusType.attack_power, 5, Stat(attack_power=64)),

    (1442274, BonusType.attack_power, 3, Stat(attack_power=48)),
    (1442274, BonusType.magic_attack, 5, Stat(magic_attack=96)),
    (1442274, BonusType.attack_power, 7, Stat(attack_power=163)),

    (1442274, BonusType.boss_damage_multiplier, 7, Stat(boss_damage_multiplier=14)),
    (1442274, BonusType.damage_multiplier, 7, Stat(damage_multiplier=7)),

]

@pytest.mark.parametrize('gear_id, bonus_type, grade, target', TEST_CASES_ARMOR + TEST_CASES_WEAPON)
def test_armor_bonus(gear_id, bonus_type, grade, target):
    repository = GearRepository()

    gear = repository.get_by_id(gear_id)
    bonus = Bonus(grade=grade, bonus_type=bonus_type)

    bonus_stat = bonus.calculate_improvement(gear)
    logger.info(gear)

    assert bonus_stat == target
