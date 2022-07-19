from collections import defaultdict
from typing import Dict

import pydantic
from bs4 import BeautifulSoup

from simaple.core.base import StatProps
from simaple.fetch.element.base import Element, ElementWrapper
from simaple.fetch.element.namespace import Namespace, PropertyNamespace, StatType
from simaple.fetch.element.provider import (
    DomElementProvider,
    MultiplierProvider,
    PotentialProvider,
    StatKeywordProvider,
)
from simaple.fetch.query import NoredirectXMLQuery


def kms_homepage_providers() -> Dict[str, DomElementProvider]:
    grades = ["레어", "에픽", "유니크", "레전드리"]
    providers = {}
    for k in [
        "STR",
        "DEX",
        "LUK",
        "INT",
        "공격력",
        "마력",
        "MaxHP",
        "MaxMP",
        "공격력",
        "마력",
    ]:
        providers[k] = StatKeywordProvider()

    for k in ["보스몬스터공격시데미지", "올스탯"]:
        providers[k] = MultiplierProvider()

    for k in [f"잠재옵션({option}아이템)" for option in grades]:
        providers[k] = PotentialProvider(type="potential")

    for k in [f"에디셔널잠재옵션({option}아이템)" for option in grades]:
        providers[k] = PotentialProvider(type="additional_potential")

    return providers


def korean_names() -> Dict[str, Namespace]:
    return {
        "STR": StatProps.STR,
        "DEX": StatProps.DEX,
        "LUK": StatProps.LUK,
        "INT": StatProps.INT,
        "STR%": StatProps.STR_multiplier,
        "DEX%": StatProps.DEX_multiplier,
        "LUK%": StatProps.LUK_multiplier,
        "INT%": StatProps.INT_multiplier,
        "STRF": StatProps.STR_static,
        "DEXF": StatProps.DEX_static,
        "LUKF": StatProps.LUK_static,
        "INTF": StatProps.INT_static,
        "MaxHP": StatProps.MHP,
        "MaxMP": StatProps.MMP,
        "공격력": StatProps.attack_power,
        "마력": StatProps.magic_attack,
        "보스몬스터공격시데미지": StatProps.boss_damage_multiplier,
        "올스탯%": PropertyNamespace.all_stat_multiplier,
        "올스탯": PropertyNamespace.all_stat,
        "데미지": StatProps.damage_multiplier,
        "몬스터방어력무시": StatProps.ignored_defence,
        "크리티컬확률": StatProps.critical_rate,
        "크리티컬데미지": StatProps.critical_damage,
    }


class ItemElement(Element):
    providers: Dict[str, DomElementProvider] = pydantic.Field(
        default_factory=kms_homepage_providers
    )
    global_providers: Dict[str, DomElementProvider] = pydantic.Field(
        default_factory=dict
    )
    names: Dict[str, Namespace] = pydantic.Field(default_factory=korean_names)

    def run(self, html_text):
        soup = BeautifulSoup(html_text, "html.parser")
        dom_elements = soup.find(class_="stet_info").find_all("li")

        stacks: Dict[StatType, Dict[str, int]] = defaultdict(list)
        for dom_element in dom_elements:
            provided = self._extract_from_dom_element(dom_element)
            # print(provided)
            for k, v in provided.items():
                stacks[k].append(v)

        return stacks

    def _extract_from_dom_element(self, dom_element) -> Dict[StatType, Dict[str, int]]:
        name = (
            dom_element.find(class_="stet_th")
            .find("span")
            .text.strip()
            .replace("\n", "")
            .replace(" ", "")
        )
        value_element = dom_element.find(class_="point_td")

        provider = self.providers.get(name)
        if provider is not None:
            return provider.get_value(name, value_element)

        return {}


def item_promise():
    return ElementWrapper(
        element=ItemElement(),
        query=NoredirectXMLQuery(),
    )
