import datetime
from typing import TypedDict, cast

import requests

from simaple.request.external.nexon.api.auth import NexonRequestAgent
from simaple.request.external.nexon.schema.character.ability import (
    CharacterAbilityResponse,
)
from simaple.request.external.nexon.schema.character.basic import (
    CharacterBasicResponse,
    CharacterStatResponse,
)
from simaple.request.external.nexon.schema.character.hyper_stat import (
    CharacterHyperStatResponse,
)


def _get_nexon_api_header(access_token: str):
    return {
        "X-Nxopen-Api-Key": access_token,
        "Accept": "application/json",
    }


def as_nexon_datetime(date: datetime.date) -> str:
    return date.strftime("%Y-%m-%d")


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


def get_character_basic(
    host: str, access_token: str, payload: CharacterIDWithDate
) -> CharacterBasicResponse:
    return requests.get(
        f"{host}/maplestory/v1/character/basic",
        headers=_get_nexon_api_header(access_token),
        params=cast(dict, payload),
        allow_redirects=True,
    ).json()


def get_character_stat(
    host: str, access_token: str, payload: CharacterIDWithDate
) -> CharacterStatResponse:
    return cast(
        CharacterStatResponse,
        requests.get(
            f"{host}/maplestory/v1/character/stat",
            headers=_get_nexon_api_header(access_token),
            params=cast(dict, payload),
            allow_redirects=True,
        ).json(),
    )


def get_hyper_stat(
    host: str, access_token: str, payload: CharacterIDWithDate
) -> CharacterHyperStatResponse:
    return cast(
        CharacterHyperStatResponse,
        requests.get(
            f"{host}/maplestory/v1/character/hyperstat",
            headers=_get_nexon_api_header(access_token),
            params=cast(dict, payload),
            allow_redirects=True,
        ).json(),
    )
