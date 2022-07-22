from collections import defaultdict
from typing import Dict, Optional

import pydantic
from bs4 import BeautifulSoup

from simaple.fetch.element.base import Element, ElementWrapper
from simaple.fetch.element.namespace import Namespace, StatType, korean_names
from simaple.fetch.element.provider import (
    DomElementProvider,
    GlobalProvider,
    MultiplierProvider,
    PotentialProvider,
    SoulWeaponProvider,
    StarforceProvider,
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

    providers["기타"] = StarforceProvider()
    providers["소울옵션"] = SoulWeaponProvider()

    return providers


class ItemElement(Element):
    providers: Dict[str, DomElementProvider] = pydantic.Field(
        default_factory=kms_homepage_providers
    )
    names: Dict[str, Namespace] = pydantic.Field(default_factory=korean_names)
    global_provider: Optional[DomElementProvider] = pydantic.Field(
        default_factory=GlobalProvider,
    )

    def run(self, html_text):
        soup = BeautifulSoup(html_text, "html.parser")
        dom_elements = soup.find(class_="stet_info").find_all("li")

        stacks: Dict[StatType, Dict[str, int]] = defaultdict(list)
        for dom_element in dom_elements:
            provided = self._extract_from_dom_element(dom_element)
            for k, v in provided.items():
                stacks[k].append(v)

        if self.global_provider:
            global_provided = self.global_provider.get_value("", soup)
            for k, v in global_provided.items():
                stacks[k].append(v)

        result = {}
        for k, list_value in stacks.items():
            if k not in (StatType.potential, StatType.additional_potential):
                if len(list_value) == 1:
                    contracted_value = list_value[0]
                else:
                    contracted_value = {}
                    for value in list_value:
                        contracted_value.update(value)
            else:
                contracted_value = list_value

            result[k.value] = contracted_value
        
        return result

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
