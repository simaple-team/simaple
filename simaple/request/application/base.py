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


def as_python_datetime(date: str) -> datetime.datetime:
    return datetime.datetime.strptime(date, "%Y-%m-%d%H:%M:%S+09:00")


class Token:
    def __init__(self, access_token: str) -> None:
        self._access_token = access_token

    @property
    def access_token(self) -> str:
        return self._access_token

    async def request(self, uri: str, param: dict[str, Any]) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{uri}",
                headers={
                    "X-Nxopen-Api-Key": self._access_token,
                    "Accept": "application/json",
                },
                params=param,
                allow_redirects=True,
            ) as resp:
                return cast(dict, await resp.json())


async def get_character_id(token: Token, name: str) -> CharacterID:
    uri = f"{HOST}/maplestory/v1/id"

    resp = await token.request(uri, {"character_name": name})
    return {
        "ocid": resp["ocid"],
        "date": datetime.datetime.now().date() - datetime.timedelta(days=2),
    }
