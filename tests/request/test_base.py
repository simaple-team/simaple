import asyncio

import pytest

from simaple.request.application.base import Token, get_character_id
from simaple.request.application.props import get_hyperstat

API_KEY = "test_931c08e3c68f6fd9a3084914d7a23cad07ecf4f5fcf67f93fcccd79eabd10d2d109b4615165332e79d3ae3e6ce793a5e"


def test_get_character_id():
    token = Token(API_KEY)
    asyncio.run(get_character_id(token, "Designate"))


@pytest.mark.asyncio
async def test_get_hyperstat():
    token = Token(API_KEY)
    character_id = await get_character_id(token, "Designate")
    hyperstat = await get_hyperstat(token, character_id)
    import json

    with open("hyperstat.json", "w") as f:
        json.dump(hyperstat, f, indent=4, ensure_ascii=False)
