import re
from typing import Dict

from bs4 import BeautifulSoup

from simaple.fetch.element.base import Element, ElementWrapper
from simaple.fetch.element.gear.extractor import (
    PropertyExtractor,
    ReduceExtractor,
    SinglePropertyExtractor,
)
from simaple.fetch.element.gear.fragment import ItemFragment
from simaple.fetch.element.gear.namespace import StatType
from simaple.fetch.element.gear.provider import (
    DomElementProvider,
    MultiplierProvider,
    PotentialProvider,
    SoulWeaponProvider,
    StarforceProvider,
    StatKeywordProvider,
)
from simaple.fetch.query import NoredirectXMLQuery


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


class GearElement(Element):
    extractors: list[PropertyExtractor]

    def run(self, html_text):
        soup = BeautifulSoup(html_text, "html.parser")
        dom_elements = soup.find(class_="stet_info").find_all("li")
        fragments = [ItemFragment(html=dom_element) for dom_element in dom_elements]
        result = {
            StatType.image: self.get_image(soup),
            StatType.name: self.get_item_name(soup),
        }

        for extractor in self.extractors:
            result.update(extractor.extract(fragments))

        return {k.value: v for k, v in result.items()}

    def get_image(self, soup: BeautifulSoup) -> str:
        image_url = soup.find(class_="item_img").find("img")["src"]

        return image_url

    def get_item_name(self, soup: BeautifulSoup) -> str:
        text = soup.find(class_="item_img").find("img")["alt"]

        improved_regex = re.compile(r"(.+)\(\+[0-9]\)")
        if improved_regex.match(text):
            return improved_regex.match(text).group(1).strip()

        return text


def item_promise():
    return ElementWrapper(
        element=GearElement(
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
