from simaple.fetch.element import MapleItemListElement
from simaple.fetch.token import TokenRepository


def test_resolve_item():
    element = MapleItemListElement()

    with open("tests/fetch/item.html") as f:
        html_text = f.read()

    result = element.run(html_text)
    print(result)
