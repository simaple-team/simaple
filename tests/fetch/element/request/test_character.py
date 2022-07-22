from simaple.fetch.query import CookiedQuery
from simaple.fetch.token import TokenRepository


def test_get_item():
    token_repository = TokenRepository()
    name = "Backend"
    token = token_repository.get(name)

    result = (
        CookiedQuery().get("/Common/Character/Detail/123", token).replace("\r\n", "\n")
    )
