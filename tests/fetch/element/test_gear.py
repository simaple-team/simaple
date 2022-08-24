from simaple.fetch.element import GearElement
from simaple.fetch.element.gear.builtin import kms_stat_providers
from simaple.fetch.element.gear.extractor import (
    ReduceExtractor,
    SinglePropertyExtractor,
)
from simaple.fetch.element.gear.namespace import StatType
from simaple.fetch.element.gear.provider import (
    PotentialProvider,
    SoulWeaponProvider,
    StarforceProvider,
)


def test_item_element():
    element = GearElement(
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
            "몬스터방어력무시": 10,
        },
        "base": {
            "INT": 60,
            "LUK": 60,
            "MaxHP": 0,
            "MaxMP": 0,
            "공격력": 143,
            "마력": 241,
            "보스몬스터공격시데미지": 30,
            "몬스터방어력무시": 10,
        },
        "bonus": {
            "INT": 20,
            "LUK": 20,
            "MaxHP": 2400,
            "MaxMP": 0,
            "공격력": 44,
            "마력": 73,
            "보스몬스터공격시데미지": 0,
            "몬스터방어력무시": 0,
        },
        "increment": {
            "INT": 49,
            "LUK": 31,
            "MaxHP": 180,
            "MaxMP": 180,
            "공격력": 45,
            "마력": 125,
            "보스몬스터공격시데미지": 0,
            "몬스터방어력무시": 0,
        },
        "potential": {
            "option": [{"마력%": 6}, {"공격시10%확률로2레벨슬로우효과적용": None}, {"데미지%": 3}],
            "raw": [
                "마력 : +6%",
                "공격 시 10% 확률로 2레벨 슬로우효과 적용",
                "데미지 : +3%",
            ],
            "grade": "에픽",
        },
        "soulweapon": {"name": "위대한 벨룸의 소울", "option": {"몬스터방어율무시%": 7}},
        "starforce": 12,
        "surprise": False,
        "name": "앱솔랩스 샤이닝로드",
        "image": {
            "url": "https://avatar.maplestory.nexon.com/ItemIcon/KENDJGPE.png",
            "gear_id": 1212115,
        },
    }
