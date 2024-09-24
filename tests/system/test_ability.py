import pytest

from simaple.core.base import ActionStat, ExtendedStat, Stat
from simaple.system.ability import (
    AbilityLine,
    get_ability_stat,
    get_ability_stat_from_line,
)


@pytest.mark.parametrize(
    "type_name, value, expected",
    [
        ("attack_power", 5, ExtendedStat(stat=Stat(attack_power=5))),
        ("magic_attack", 5, ExtendedStat(stat=Stat(magic_attack=5))),
        (
            "boss_damage_multiplier",
            5,
            ExtendedStat(stat=Stat(boss_damage_multiplier=5)),
        ),
        (
            "abnormal_status_damage_multiplier",
            5,
            ExtendedStat(stat=Stat(boss_damage_multiplier=5)),
        ),
        ("cooldown_reset_chance", 5, ExtendedStat()),
        ("buff_duration", 5, ExtendedStat(action_stat=ActionStat(buff_duration=5))),
    ],
)
def test_ability(type_name, value, expected):
    line = AbilityLine(type=type_name, value=value)

    assert get_ability_stat_from_line(line) == expected


def test_ability_stat():
    lines = [
        AbilityLine(type="boss_damage_multiplier", value=20),
        AbilityLine(type="buff_duration", value=37),
        AbilityLine(type="abnormal_status_damage_multiplier", value=8),
    ]

    result = get_ability_stat(lines)
    assert result == ExtendedStat(action_stat=ActionStat(buff_duration=37), stat=Stat(boss_damage_multiplier=28))
