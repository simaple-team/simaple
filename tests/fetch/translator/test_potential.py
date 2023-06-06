import pytest

from simaple.core import LevelStat, Stat
from simaple.fetch.translator.kms.potential import kms_potential_translator


@pytest.mark.parametrize(
    "expression, expected_stat",
    [
        ("DEX : +9%", Stat(DEX_multiplier=9)),
        ("INT : +6%", Stat(INT_multiplier=6)),
        ("STR : +3%", Stat(STR_multiplier=3)),
        ("LUK : +12%", Stat(LUK_multiplier=12)),
        ("몬스터 방어율 무시 : +35%", Stat(ignored_defence=35)),
        ("방어력 : +60", Stat()),
        ("공격력 : +10", Stat(attack_power=10)),
        ("DEX : +6", Stat(DEX=6)),
        ("올스탯 : +3%", Stat.all_stat_multiplier(3)),
        ("캐릭터 기준 9레벨 당 DEX : +1", LevelStat(DEX=1)),
        ("최대 HP : +9%", Stat(MHP_multiplier=9)),
        ("아이템 드롭률 : +20%", Stat()),
        ("이동속도 : +4", Stat()),
        ("점프력 : +4", Stat()),
    ],
)
def test_potential_translator(expression, expected_stat):
    translator = kms_potential_translator()
    result = translator.translate_expression(expression)
    assert expected_stat == result
