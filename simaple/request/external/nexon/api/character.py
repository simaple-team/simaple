from typing import TypedDict, cast

import requests

from simaple.request.external.nexon.api.auth import NexonRequestAgent
from simaple.request.external.nexon.schema.character.ability import (
    CharacterAbilityResponse,
)


def _get_nexon_api_header(access_token: str):
    return {
        "X-Nxopen-Api-Key": access_token,
        "Accept": "application/json",
    }


class CharacterIDWithDate(TypedDict):
    ocid: str
    date: str


def get_character_ocid(
    host: str,
    access_token: str,
    name: str,
) -> str:
    resp = requests.get(
        f"{host}/maplestory/v1/id",
        headers=_get_nexon_api_header(access_token),
        params={"character_name": name},
        allow_redirects=True,
    ).json()

    return resp["ocid"]


def get_character_ability(
    host: str, access_token: str, payload: CharacterIDWithDate
) -> CharacterAbilityResponse:
    return cast(
        CharacterAbilityResponse,
        requests.get(
            f"{host}/maplestory/v1/character/ability",
            headers=_get_nexon_api_header(access_token),
            params=cast(dict, payload),
            allow_redirects=True,
        ).json(),
    )
