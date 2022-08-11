import pytest

from simaple.core import Stat
from simaple.fetch.translator.kms.gear import kms_gear_stat_translator


@pytest.mark.parametrize(
    "parsed_stat, expected_stat",
    [
        (
            {
                "STR": 36,
                "DEX": 33,
                "INT": 31,
                "LUK": 25,
                "MaxHP": 130,
                "공격력": 12,
                "마력": 3,
            },
            Stat(
                STR=36,
                DEX=33,
                INT=31,
                LUK=25,
                MHP=130,
                attack_power=12,
                magic_attack=3,
            ),
        ),
        (
            {
                "STR": 36,
            },
            Stat(
                STR=36,
            ),
        ),
        (
            {
                "INT": 36,
            },
            Stat(
                INT=36,
            ),
        ),
        (
            {
                "마력": 36,
            },
            Stat(
                magic_attack=36,
            ),
        ),
        (
            {
                "STR": 339,
                "DEX": 327,
                "MaxHP": 255,
                "MaxMP": 255,
                "공격력": 789,
                "보스몬스터공격시데미지": 40,
                "몬스터방어력무시": 10,
            },
            Stat(
                STR=339,
                DEX=327,
                MHP=255,
                MMP=255,
                attack_power=789,
                boss_damage_multiplier=40,
                ignored_defence=10,
            ),
        ),
    ],
)
def test_potential_translator(parsed_stat, expected_stat):
    translator = kms_gear_stat_translator()
    result = translator.translate(parsed_stat)
    assert expected_stat == result
