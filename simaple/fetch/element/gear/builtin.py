from typing import Dict

from simaple.fetch.element.base import ElementWrapper
from simaple.fetch.element.gear.element import GearElement
from simaple.fetch.element.gear.extractor import (
    ReduceExtractor,
    SinglePropertyExtractor,
)
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
    providers: Dict[str, DomElementProvider] = {}
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

    for k in ["보스몬스터공격시데미지", "올스탯", "몬스터방어력무시", "몬스터방어율무시"]:
        providers[k] = MultiplierProvider()

    return providers


def standard_gear_element():
    return GearElement(
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
                target=StatType.surprise, providers={"기타": StarforceProvider()}
            ),
            SinglePropertyExtractor(
                target=StatType.soulweapon, providers={"소울옵션": SoulWeaponProvider()}
            ),
        ]
    )


def standard_gear_promise():
    return ElementWrapper(
        element=standard_gear_element(),
        query=NoredirectXMLQuery(),
    )
