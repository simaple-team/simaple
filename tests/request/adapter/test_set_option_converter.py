import pytest

from simaple.core import Stat
from simaple.request.adapter.gear_loader._set_item_converter import (
    parse_set_option_text_into_stat,
)


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "최대 HP : +1500, 최대 MP : +1500, 공격력 : +20, 마력 : +20, 보스 몬스터 공격 시 데미지 : +10%",
            Stat(
                MHP=1500,
                MMP=1500,
                attack_power=20,
                magic_attack=20,
                boss_damage_multiplier=10,
            ),
        ),
        (
            "올스탯 : +30, 공격력 : +20, 마력 : +20, 보스 몬스터 공격 시 데미지 : +10%",
            Stat(
                STR=30,
                DEX=30,
                INT=30,
                LUK=30,
                attack_power=20,
                magic_attack=20,
                boss_damage_multiplier=10,
            ),
        ),
        (
            "공격력 : +25, 마력 : +25, 방어력 : +200, 몬스터 방어율 무시 : +10%",
            Stat(attack_power=25, magic_attack=25, ignored_defence=10),
        ),
        (
            "공격력 : +30, 마력 : +30, 보스 몬스터 공격 시 데미지 : +10%",
            Stat(attack_power=30, magic_attack=30, boss_damage_multiplier=10),
        ),
        (
            "최대 HP : +20%, 최대 MP : +20%, 공격력 : +20, 마력 : +20",
            Stat(
                MHP_multiplier=20, MMP_multiplier=20, attack_power=20, magic_attack=20
            ),
        ),
        (
            "공격력 : +20, 마력 : +20, 몬스터 방어율 무시 : +10%",
            Stat(attack_power=20, magic_attack=20, ignored_defence=10),
        ),
        ("<포니 파워 Lv.3> 스킬 사용 가능", Stat()),
        (
            "올스탯 : +10, 최대 HP : +500, 최대 MP : +500, 공격력 : +7, 마력 : +7",
            Stat(
                STR=10,
                DEX=10,
                INT=10,
                LUK=10,
                MHP=500,
                MMP=500,
                attack_power=7,
                magic_attack=7,
            ),
        ),
        (
            "올스탯 : +5, 공격력 : +3, 마력 : +3",
            Stat(STR=5, DEX=5, INT=5, LUK=5, attack_power=3, magic_attack=3),
        ),
        ("몬스터 방어율 무시 : +10%", Stat(ignored_defence=10)),
        ("방어력 : +200", Stat()),
        (
            "올스탯 : +50, 공격력 : +40, 마력 : +40, 방어력 : +600, 보스 몬스터 공격 시 데미지 : +10%",
            Stat(
                STR=50,
                DEX=50,
                INT=50,
                LUK=50,
                attack_power=40,
                magic_attack=40,
                boss_damage_multiplier=10,
            ),
        ),
        (
            (
                "STR : +20, DEX : +20, 최대 HP : +1000, 최대 MP : +1000",
                Stat(STR=20, DEX=20, MHP=1000, MMP=1000),
            )
        ),
    ],
)
def test_get_pet_option_value_and_type(value, expected):
    assert parse_set_option_text_into_stat(value) == expected
