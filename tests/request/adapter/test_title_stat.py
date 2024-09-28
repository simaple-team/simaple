import pytest

from simaple.core import Stat
from simaple.request.adapter.gear_loader._gearset_converter import parse_title_stat


@pytest.mark.parametrize(
    "title, expected",
    [
        (
            "예티와 핑크빈 모두 내 마음 한구석에 남아있네. 예티와 핑크빈을 추억하며.\n올스탯 +20\n최대 HP/최대 MP +1000\n공격력/마력+10\n보스 몬스터 공격 시 데미지+10% \n\n클릭으로 ON/OFF시킬 수 있다.",
            Stat(
                STR=20,
                DEX=20,
                INT=20,
                LUK=20,
                MHP=1000,
                MMP=1000,
                attack_power=10,
                magic_attack=10,
                boss_damage_multiplier=10,
            ),
        )
    ],
)
def test_title_to_stat(title, expected):
    assert parse_title_stat(title) == expected
