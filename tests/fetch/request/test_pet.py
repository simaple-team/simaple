import asyncio

from simaple.fetch.query import CookiedQuery, NoredirectXMLQuery
from simaple.fetch.token import TokenRepository


def test_get_pet_gearset():
    token_repository = TokenRepository()
    name = "생분자"
    token = token_repository.get(name)

    asyncio.run(CookiedQuery().get("/Common/Character/Detail/123/Pet", token))


def test_get_pet_item():
    token_repository = TokenRepository()
    name = "Backend"
    token = token_repository.get(name)

    asyncio.run(
        NoredirectXMLQuery().get(
            # pylint: disable=C0301
            "/Common/Resource/Item?p=ufLJEUIu7%2f0y9jJyTpI0%2b%2bA5dsW4%2b6gPH1ja5lz8WhOzFAqkeVZY8QLjLxnrs95PWMgk7SNF3EXia9bHzUhku0EjKCmlb8XtzMRoHHT48pmXjWJhxZu7GSEHEvjCezyFJv%2fHQsbIAkhSrkB8uclYMkF%2brEIC2BtwSGoTWOxbiJRiAhp9I6e%2fZegL%2b1l904Ek6LIsJfD8%2b6o7ZxYqxzQo1nzEc1lLe8XUf9WsoaGrsUIlZ7Lmz%2blf4XKCgzUkuX2u2N0N3Px01g%2bNNsLcDfm9A5aZ2yHCqVcUgqUPgnaiajflvGLmb%2fILyHGEgu1v3htnb6%2fRieN4dOKTutv48ciHug%3d%3d",
            token,
        )
    )
