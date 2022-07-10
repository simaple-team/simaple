from simaple.fetch.token import TokenRepository
from simaple.fetch.element import MapleItemListElement


def test_resolve_item():
    element = MapleItemListElement()

    with open("tests/fetch/item.html") as f:
        html_text = f.read()

    result = element.run(html_text)
    print(result)

'''
def test_get_item():
    token_repository = TokenRepository()
    name = "Backend"
    token = token_repository.get(name)

    element = MapleItemListElement()

    v = element.fetch(token=token)
    result = element.run(v)
'''