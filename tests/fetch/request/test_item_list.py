import asyncio

from simaple.fetch.query import CookiedQuery
from simaple.fetch.token import TokenRepository


def test_get_item():
    token_repository = TokenRepository()
    name = "Backend"
    token = token_repository.get(name)

    asyncio.run(CookiedQuery().get("/Common/Character/Detail/123/Equipment", token))
