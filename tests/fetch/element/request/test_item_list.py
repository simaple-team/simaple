from simaple.fetch.element import MapleItemListElement
from simaple.fetch.token import TokenRepository


def test_get_item():
    token_repository = TokenRepository()
    name = "Backend"
    token = token_repository.get(name)

    element = MapleItemListElement()

    v = element.fetch(token=token)
    element.run(v)
