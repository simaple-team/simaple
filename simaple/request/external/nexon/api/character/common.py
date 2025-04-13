from typing import TypedDict, cast

import requests
import aiohttp

class CharacterIDWithDate(TypedDict):
    ocid: str
    date: str


def get_nexon_api_header(access_token: str):
    return {
        "X-Nxopen-Api-Key": access_token,
        "Accept": "application/json",
    }


def get_character_ocid(
    host: str,
    access_token: str,
    name: str,
) -> str:
    resp = requests.get(
        f"{host}/maplestory/v1/id",
        headers=get_nexon_api_header(access_token),
        params={"character_name": name},
        allow_redirects=True,
    ).json()

    return cast(str, resp["ocid"])



async def get_character_ocid_async(
    session: aiohttp.ClientSession,
    host: str,
    access_token: str,
    name: str,
) -> str | None:
    """
    returns ocid if the character is found.
    returns None if the character is not found.
    """
    async with session.get(
        f"{host}/maplestory/v1/id",
        headers=get_nexon_api_header(access_token),
        params={"character_name": name},
        allow_redirects=True,
    ) as response:
        resp = await response.json()

    try:
        return cast(str, resp["ocid"])
    except KeyError:
        return None
