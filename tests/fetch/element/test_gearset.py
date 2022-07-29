from simaple.fetch.element import MapleGearsetElement


def test_resolve_item():
    element = MapleGearsetElement()

    with open("tests/fetch/item.html", encoding="euc-kr") as f:
        html_text = f.read()

    result = element.run(html_text)
    print(result)
