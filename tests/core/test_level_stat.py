import pytest

from simaple.core import LevelStat, Stat

TEST_CASES = [
    ("STR", 4, 260, Stat(STR=104)),
    ("STR", 4, 265, Stat(STR=104)),
    ("attack_power", 5, 200, Stat(attack_power=100)),
]


@pytest.mark.parametrize("stat_name, value, level, expected", TEST_CASES)
def test_ability(stat_name, value, level, expected):
    level_stat = LevelStat(**{stat_name: value})

    assert level_stat.get_stat(level) == expected


def test_sum():
    level_stat_a = LevelStat(STR=1, LUK=1, INT=1, DEX=1, attack_power=2, magic_attack=2)

    level_stat_b = LevelStat(
        STR=11, LUK=11, INT=11, DEX=11, attack_power=22, magic_attack=22
    )

    assert level_stat_a + level_stat_b == LevelStat(
        STR=12, LUK=12, INT=12, DEX=12, attack_power=24, magic_attack=24
    )


def test_complex_get_stat():
    level_stat = LevelStat(STR=1, LUK=1, INT=1, DEX=1, attack_power=2, magic_attack=2)

    assert level_stat.get_stat(250) == Stat(
        STR=25,
        LUK=25,
        INT=25,
        DEX=25,
        attack_power=50,
        magic_attack=50,
    )
