from simaple.fetch.element import GearElement


def test_item_element():
    element = GearElement()

    with open("tests/fetch/resources/arcane_symbol.html", encoding="euc-kr") as f:
        html_text = f.read()

    result = element.run(html_text)
    print(result)
