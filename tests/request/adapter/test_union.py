import pytest

from simaple.core import ActionStat, ExtendedStat, Stat
from simaple.request.adapter.union_loader._converter import (
    get_stat_from_occupation_description,
)
from simaple.request.adapter.union_loader.adapter import (
    get_union_squad,
    get_union_squad_effect,
)


def test_union_raiders_response(character_union_raiders_response):
    union_squad = get_union_squad(character_union_raiders_response)
    squad_effect = get_union_squad_effect(character_union_raiders_response)

    assert union_squad.get_stat().short_dict() == squad_effect.stat.short_dict()


@pytest.mark.parametrize(
    "expression, expected",
    [
        ("크리티컬 데미지 20.00% 증가", ExtendedStat(stat=Stat(critical_damage=20.00))),
        ("INT 25 증가", ExtendedStat(stat=Stat(INT_static=25))),
        ("LUK 5 증가", ExtendedStat(stat=Stat(LUK_static=5))),
        (
            "보스 몬스터 공격 시 데미지 40% 증가",
            ExtendedStat(stat=Stat(boss_damage_multiplier=40)),
        ),
        ("마력 5 증가", ExtendedStat(stat=Stat(magic_attack=5))),
        ("공격력 15 증가", ExtendedStat(stat=Stat(attack_power=15))),
        (
            "버프 지속시간 40% 증가",
            ExtendedStat(action_stat=ActionStat(buff_duration=40)),
        ),
        ("방어율 무시 39% 증가", ExtendedStat(stat=Stat(ignored_defence=39))),
    ],
)
def test_union_occupation_parse(expression, expected):
    assert get_stat_from_occupation_description(expression) == expected
