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
            Stat(
                STR=45 + 25,
                INT=54 + 25,
            )
            + Stat.all_stat_multiplier(5),
            [
                bonus.SingleStatBonus(grade=5, stat_type=BaseStatType.STR),
                bonus.SingleStatBonus(grade=6, stat_type=BaseStatType.INT),
                bonus.DualStatBonus(
                    grade=5,
                    stat_type_pair=(
                        BaseStatType.STR,
                        BaseStatType.INT,
                    ),
                ),
                bonus.AllstatBonus(grade=5),
            ],
        ),
        (
            "앱솔랩스 메이지케이프",
            Stat(
                STR=54 + 15,
                INT=63 + 15,
            ),
            [
                bonus.SingleStatBonus(grade=6, stat_type=BaseStatType.STR),
                bonus.SingleStatBonus(grade=7, stat_type=BaseStatType.INT),
                bonus.DualStatBonus(
                    grade=3,
                    stat_type_pair=(
                        BaseStatType.STR,
                        BaseStatType.INT,
                    ),
                ),
            ],
        ),
        (
            "앱솔랩스 스펠링스태프",
            Stat(damage_multiplier=4, boss_damage_multiplier=10) + Stat.all_stat_multiplier(5),
            [
                bonus.BossDamageMultiplierBonus(grade=5),
                bonus.DamageMultiplierBonus(grade=4),
                bonus.AllstatBonus(grade=5),
            ],
        ),
        (
            "앱솔랩스 스펠링스태프",
            Stat(damage_multiplier=4, boss_damage_multiplier=10, MHP=480 * 5, MMP=480 * 5),
            [
                bonus.ResourcePointBonus(stat_type="MHP", grade=5),
                bonus.ResourcePointBonus(stat_type="MMP", grade=5),
                bonus.BossDamageMultiplierBonus(grade=5),
                bonus.DamageMultiplierBonus(grade=4),
            ],
        ),
        (
            "파프니르 마나크래들",
            Stat(magic_attack=49, attack_power=83),
            [
                bonus.AttackTypeBonus(attack_type=AttackType.attack_power, grade=7),
                bonus.AttackTypeBonus(attack_type=AttackType.magic_attack, grade=5),
            ],
        ),
        (
            "파프니르 마나크래들",
            Stat(magic_attack=49, attack_power=83, INT=48 + 24, STR=24),
            [
                bonus.SingleStatBonus(grade=6, stat_type=BaseStatType.INT),
                bonus.DualStatBonus(
                    grade=6,
                    stat_type_pair=(
                        BaseStatType.STR,
                        BaseStatType.INT,
                    ),
                ),
                bonus.AttackTypeBonus(attack_type=AttackType.attack_power, grade=7),
                bonus.AttackTypeBonus(attack_type=AttackType.magic_attack, grade=5),
            ],
        ),
    ],
)
def test_bonus(gear_name, stat, expected):
    gear_repository = GearRepository()
    calculator = BonusCalculator()

    gear = gear_repository.get_by_name(gear_name)
    result = calculator.compute(stat, gear)

    assert expected == result
