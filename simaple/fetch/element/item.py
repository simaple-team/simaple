from typing import Dict, Optional

import pydantic
from bs4 import BeautifulSoup

from simaple.fetch.element.base import Element, ElementWrapper
from simaple.fetch.element.namespace import Namespace, StatType, korean_names
from simaple.fetch.element.provider import (
    DomElementProvider,
    GlobalProvider,
    ItemFragment,
    MultiplierProvider,
    PotentialProvider,
    PropertyExtractor,
    ReduceExtractor,
    SinglePropertyExtractor,
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


def kms_stat_providers() -> Dict[str, DomElementProvider]:
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

    return providers


class ItemElement(Element):
    extractors: list[PropertyExtractor]
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
        fragments = [ItemFragment(html=dom_element) for dom_element in dom_elements]
        result = {}

        for extractor in self.extractors:
            result.update(extractor.extract(fragments))

        if self.global_provider:
            result.update(self.global_provider.get_value(ItemFragment(html=soup)))

        return {k.value: v for k, v in result.items()}


def item_promise():
    return ElementWrapper(
        element=ItemElement(
            extractors=[
                ReduceExtractor(providers=kms_stat_providers()),
                SinglePropertyExtractor(
                    target=StatType.potential,
                    providers={
                        f"잠재옵션({option}아이템)": PotentialProvider(type="potential")
                        for option in ("레어", "에픽", "유니크", "레전드리")
                    },
                ),
                SinglePropertyExtractor(
                    target=StatType.additional_potential,
                    providers={
                        f"에디셔널잠재옵션({option}아이템)": PotentialProvider(
                            type="additional_potential"
                        )
                        for option in ("레어", "에픽", "유니크", "레전드리")
                    },
                ),
                SinglePropertyExtractor(
                    target=StatType.starforce, providers={"기타": StarforceProvider()}
                ),
                SinglePropertyExtractor(
                    target=StatType.soulweapon, providers={"소울옵션": SoulWeaponProvider()}
                ),
            ]
        ),
        query=NoredirectXMLQuery(),
    )
