# pylint: disable=C0301
from typing import Dict

import pytest
from bs4 import BeautifulSoup

from simaple.fetch.element.namespace import StatType
from simaple.fetch.element.provider import (
    DomElementProvider,
    MultiplierProvider,
    PotentialProvider,
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
        {StatType.potential: {"마력%": 6, "공격시10%확률로2레벨슬로우효과적용": None, "DEX%": 3}},
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
]


@pytest.mark.parametrize("provider, expected, html", fixtures)
def test_provider(
    provider: DomElementProvider, expected: Dict[StatType, Dict[str, int]], html: str
):
    dom_element = BeautifulSoup(html, "html.parser")
    name = (
        dom_element.find(class_="stet_th")
        .find("span")
        .text.strip()
        .replace("\n", "")
        .replace(" ", "")
    )
    value_element = dom_element.find(class_="point_td")

    result = provider.get_value(name, value_element)
    assert result == expected
