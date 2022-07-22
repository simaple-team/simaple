from simaple.fetch.element import ItemElement
from simaple.fetch.element.item import kms_stat_providers
from simaple.fetch.element.namespace import StatType
from simaple.fetch.element.provider import (
    PotentialProvider,
    ReduceExtractor,
    SinglePropertyExtractor,
    SoulWeaponProvider,
    StarforceProvider,
)


def test_item_element():
    element = ItemElement(
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
    )

    with open("tests/fetch/resources/item/16.html", encoding="euc-kr") as f:
        html_text = f.read()

    result = element.run(html_text)

    assert result == {
        "sum": {
            "INT": 129,
            "LUK": 111,
            "MaxHP": 2580,
            "MaxMP": 180,
            "공격력": 232,
            "마력": 439,
            "보스몬스터공격시데미지": 30,
        },
        "base": {
            "INT": 60,
            "LUK": 60,
            "MaxHP": 0,
            "MaxMP": 0,
            "공격력": 143,
            "마력": 241,
            "보스몬스터공격시데미지": 30,
        },
        "bonus": {
            "INT": 20,
            "LUK": 20,
            "MaxHP": 2400,
            "MaxMP": 0,
            "공격력": 44,
            "마력": 73,
            "보스몬스터공격시데미지": 0,
        },
        "increment": {
            "INT": 49,
            "LUK": 31,
            "MaxHP": 180,
            "MaxMP": 180,
            "공격력": 45,
            "마력": 125,
            "보스몬스터공격시데미지": 0,
        },
        "potential": {0: {"마력%": 6}, 1: {"공격시10%확률로2레벨슬로우효과적용": None}, 2: {"데미지%": 3}},
        "soulweapon": {"name": "위대한 벨룸의 소울", "option": {"몬스터방어율무시%": 7}},
        "starforce": 12,
        "name": "앱솔랩스 샤이닝로드",
        "image": "https://avatar.maplestory.nexon.com/ItemIcon/KENDJGPE.png",
    }
