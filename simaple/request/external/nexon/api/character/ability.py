from typing import TypedDict, cast

import requests

from simaple.request.external.nexon.api.character.common import (
    CharacterIDWithDate,
    get_nexon_api_header,
)


class _CharacterAbilityLineResponse(TypedDict):
    ability_no: str
    ability_grade: str
    ability_value: str


class _AbilityPreset(TypedDict):
    ability_info: list[_CharacterAbilityLineResponse]
    ability_preset_grade: str


class CharacterAbilityResponse(TypedDict):
    date: str
    ability_grade: str
    ability_info: list[_CharacterAbilityLineResponse]
    remain_fame: float
    preset_no: int
    ability_preset_1: _AbilityPreset
    ability_preset_2: _AbilityPreset
    ability_preset_3: _AbilityPreset


def get_character_ability(
    host: str, access_token: str, payload: CharacterIDWithDate
) -> CharacterAbilityResponse:
    return cast(
        CharacterAbilityResponse,
        requests.get(
            f"{host}/maplestory/v1/character/ability",
            headers=get_nexon_api_header(access_token),
            params=cast(dict, payload),
            allow_redirects=True,
        ).json(),
    )
