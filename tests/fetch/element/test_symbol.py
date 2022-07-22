from simaple.fetch.element import ItemElement
from simaple.fetch.token import TokenRepository


def test_item_element():
    element = ItemElement()

    with open("tests/fetch/resources/arcane_symbol.html") as f:
        html_text = f.read()

    result = element.run(html_text)
    print(result)
