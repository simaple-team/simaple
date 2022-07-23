# pylint: disable=C0301
from typing import Dict

import pytest
from bs4 import BeautifulSoup

from simaple.fetch.element.gear.namespace import StatType
from simaple.fetch.element.gear.provider import (
    DomElementProvider,
    ItemFragment,
    MultiplierProvider,
    PotentialProvider,
    SoulWeaponProvider,
    StarforceProvider,
    StatKeywordProvider,
)

fixtures = [
    (
        StatKeywordProvider(),
        {
            StatType.sum: {"DEX": 10},
            StatType.base: {"DEX": 10},
            StatType.bonus: {"DEX": 0},
            StatType.increment: {"DEX": 0},
        },
        """<li><div class="stet_th"><span>DEX</span></div><div class="point_td">+10</div></li>""",
    ),
    (
        StatKeywordProvider(),
        {
            StatType.sum: {"공격력": 2},
            StatType.base: {"공격력": 2},
            StatType.bonus: {"공격력": 0},
            StatType.increment: {"공격력": 0},
        },
        """<li><div class="stet_th"><span>공격력</span></div><div class="point_td">+2</div></li>""",
    ),
    (
        StatKeywordProvider(),
        {
            StatType.sum: {"마력": 232},
            StatType.base: {"마력": 143},
            StatType.bonus: {"마력": 44},
            StatType.increment: {"마력": 45},
        },
        """<li><div class="stet_th"><span>마력</span></div><div class="point_td"><font color='SkyBlue'>+232</font> (143 <font color='SkyBlue'>+ 44 + 45</font>)</div></li>""",
    ),
    (
        MultiplierProvider(),
        {
            StatType.sum: {"보스몬스터공격시데미지": 30},
            StatType.base: {"보스몬스터공격시데미지": 30},
            StatType.bonus: {"보스몬스터공격시데미지": 0},
            StatType.increment: {"보스몬스터공격시데미지": 0},
        },
        """<li><div class="stet_th"><span>보스 몬스터<br />공격 시 데미지</span></div><div class="point_td">+30%</div></li>""",
    ),
    (
        MultiplierProvider(),
        {
            StatType.sum: {"몬스터방어력무시": 10},
            StatType.base: {"몬스터방어력무시": 10},
            StatType.bonus: {"몬스터방어력무시": 0},
            StatType.increment: {"몬스터방어력무시": 0},
        },
        """<li><div class="stet_th"><span>몬스터 방어력 무시</span></div><div class="point_td">+10%</div></li>""",
    ),
    (
        PotentialProvider(type=StatType.potential),
        {
            StatType.potential: {
                "option": [
                    {"마력%": 6},
                    {"공격시10%확률로2레벨슬로우효과적용": None},
                    {"DEX%": 3},
                ],
                "grade": "에픽",
                "raw": [
                    "마력 : +6%",
                    "공격 시 10% 확률로 2레벨 슬로우효과 적용",
                    "DEX : +3%",
                ],
            }
        },
        """
    <li>
        <div class="stet_th">
            <span>
                잠재옵션
                    <br />
                    (<font color="Purple">에픽</font> 아이템)
            </span>
        </div>
        <div class="point_td">마력 : +6%<br/>공격 시 10% 확률로 2레벨 슬로우효과 적용<br/>DEX : +3%</div>
    </li>
    """,
    ),
    (
        StarforceProvider(),
        {StatType.starforce: 0, StatType.surprise: False},
        """<li><div class="stet_th"><span>기타</span></div><div class="point_td"><font color='Orange'>고유 아이템<br>월드 내 나의 캐릭터 간 1회 이동 가능 (이동 후 교환불가)<br></font><font color='Orange'>어드벤쳐 크리티컬링, 어드벤쳐 다크 크리티컬링, 제로 그라테스링, 다크 어드벤쳐 크리티컬링, 어드벤처 딥다크 크리티컬링은 중복 착용이 불가능합니다.</font></div></li>""",
    ),
    (
        StarforceProvider(),
        {StatType.starforce: 12, StatType.surprise: False},
        """<li><div class="stet_th"><span>기타</span></div><div class="point_td"><font color='Orange'>교환 불가<br></font>12성 강화 적용 최대 25성까지 강화 가능<br/><font color='Orange'><font color='#D57300'>플래티넘 카르마의 가위를 사용하면 1회 교환이 가능하게 할 수 있습니다.</font></font></div></li>""",
    ),
    (
        SoulWeaponProvider(),
        {StatType.soulweapon: {"name": "위대한 벨룸의 소울", "option": {"몬스터방어율무시%": 7}}},
        """<li><div class="stet_th"><span>소울옵션</span></div><div class="point_td"><font color=Gold>위대한 벨룸의 소울 적용</font><br>몬스터 방어율 무시 : +7%<br><font color=Orange>소울 충전 시 '주니어 벨룸 소환!' 사용가능</font></div></li>""",
    ),
]


@pytest.mark.parametrize("provider, expected, html", fixtures)
def test_provider(
    provider: DomElementProvider, expected: Dict[StatType, Dict[str, int]], html: str
):
    dom_element = BeautifulSoup(html, "html.parser")
    fragment = ItemFragment(html=dom_element)

    result = provider.get_value(fragment)
    assert result == expected
