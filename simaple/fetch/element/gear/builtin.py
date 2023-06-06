from typing import Dict, Literal, NewType, TypedDict

from simaple.fetch.element.base import Promise
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

StatPrecursor = NewType("StatPrecursor", dict[str, int])


class Image_(TypedDict):
    url: str
    gear_id: int


class Potential_(TypedDict):
    option: list[StatPrecursor]
    raw: list[str]
    grade: Literal["레어", "에픽", "유니크", "레전드리"]


class SoulWeapon_(TypedDict):
    name: str
    option: StatPrecursor


class GearResponse(TypedDict):
    image: Image_
    name: str
    sum: StatPrecursor
    base: StatPrecursor
    bonus: StatPrecursor
    increment: StatPrecursor
    potential: Potential_
    additional_potential: Potential_
    starforce: int
    surprise: bool
    soulweapon: StatPrecursor


def kms_stat_providers() -> Dict[str, DomElementProvider]:
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
    return Promise(
        element=standard_gear_element(),
        query=NoredirectXMLQuery(),
    )
