from typing import TypedDict, cast

import requests

from simaple.request.external.nexon.api.character.common import (
    CharacterIDWithDate,
    get_nexon_api_header,
)


class CharacterBasicResponse(TypedDict):
    date: str
    character_name: str
    world_name: str
    character_gender: str
    character_class: str
    character_class_level: str
    character_level: int
    character_exp: int
    character_exp_rate: str
    character_guild_name: str
    character_image: str
    character_date_create: str
    access_flag: str
    liberation_quest_clear_flag: str


class _CharacterFinalStat(TypedDict):
    stat_name: str
    stat_value: str


class CharacterStatResponse(TypedDict):
    date: str
    character_class: str
    final_stat: list[_CharacterFinalStat]
    remain_ap: int


def get_character_basic(
    host: str, access_token: str, payload: CharacterIDWithDate
) -> CharacterBasicResponse:
    return cast(
        CharacterBasicResponse,
        requests.get(
            f"{host}/maplestory/v1/character/basic",
            headers=get_nexon_api_header(access_token),
            params=cast(dict, payload),
            allow_redirects=True,
        ).json(),
    )


def get_character_stat(
    host: str, access_token: str, payload: CharacterIDWithDate
) -> CharacterStatResponse:
    return cast(
        CharacterStatResponse,
        requests.get(
            f"{host}/maplestory/v1/character/stat",
            headers=get_nexon_api_header(access_token),
            params=cast(dict, payload),
            allow_redirects=True,
        ).json(),
    )
