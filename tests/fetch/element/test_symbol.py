from simaple.fetch.element.gear import standard_gear_element


def test_item_element():
    element = standard_gear_element()

    with open("tests/fetch/resources/arcane_symbol.html", encoding="euc-kr") as f:
        html_text = f.read()

    result = element.run(html_text)
    assert result == {
        "image": {
            "url": "https://avatar.maplestory.nexon.com/ItemIcon/KEIDJHOA.png",
            "gear_id": 1712001,
        },
        "name": "아케인심볼 : 소멸의 여로",
        "sum": {"INT": 700},
        "base": {"INT": 0},
        "bonus": {"INT": 0},
        "increment": {"INT": 700},
        "starforce": 0,
        "surprise": False,
    }
