from simaple.fetch.element import ItemElement


def test_item_element():
    element = ItemElement()

    with open("tests/fetch/resources/item/16.html", encoding="euc-kr") as f:
        html_text = f.read()

    result = element.run(html_text)
    print(result)
