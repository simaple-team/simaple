import asyncio
import datetime
from typing import Any, TypedDict, cast

import aiohttp

HOST = "https://open.api.nexon.com"

URIS = {
    "get_character_id": "https://maplestory.nexon.com/Common/Character/GetCharacterId",
}


class CharacterID(TypedDict):
    ocid: str
    date: datetime.date


def get_character_id_param(character_id: CharacterID) -> dict:
    return {
        "ocid": character_id["ocid"],
        "date": character_id["date"].strftime("%Y-%m-%d"),
    }


class Token:
    def __init__(self, access_token: str) -> None:
        self._access_token = access_token

    @property
    def access_token(self) -> str:
        return self._access_token

    async def request(self, uri: str, param: dict[str, Any]) -> dict:
        print(param)
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                uri,
                headers={
                    "X-Nxopen-Api-Key": self._access_token,
                    "Accept": "application/json",
                },
                params=param,
                allow_redirects=False,
            )

        return await cast(dict, response.json())


async def get_character_id(token: Token, name: str) -> CharacterID:
    uri = f"{HOST}/maplestory/v1/id"

    resp = await token.request(uri, {"character_name": name})
    return {
        "ocid": resp["ocid"],
        "date": datetime.datetime.now().date() - datetime.timedelta(days=1),
    }
