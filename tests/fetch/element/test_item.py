from simaple.fetch.element import ItemElement


def test_item_element():
    element = ItemElement()

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
        "potential": [{0: {"마력": 6}, 1: {"공격시10%확률로2레벨슬로우효과적용": None}, 2: {"데미지": 3}}],
        "soulweapon": {"name": "위대한 벨룸의 소울", "option": {"몬스터방어율무시%": 7}},
        "starforce": 12,
        "name": "앱솔랩스 샤이닝로드",
        "image": "https://avatar.maplestory.nexon.com/ItemIcon/KENDJGPE.png",
    }
