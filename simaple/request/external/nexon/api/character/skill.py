from typing import TypedDict, cast

import requests

from simaple.request.external.nexon.api.character.common import (
    CharacterIDWithDate,
    get_nexon_api_header,
)


class CharacterSkillDescription(TypedDict):
    skill_name: str
    skill_description: str
    skill_level: int
    skill_effect: str | None
    skill_icon: str
    skill_effect_next: str


class CharacterSkillResponse(TypedDict):
    date: str
    character_class: str
    character_skill_grade: str
    character_skill: list[CharacterSkillDescription]


class AggregatedCharacterSkillResponse(TypedDict):
    response_at_0: CharacterSkillResponse
    response_at_1: CharacterSkillResponse
    response_at_1_and_half: CharacterSkillResponse
    response_at_2: CharacterSkillResponse
    response_at_2_and_half: CharacterSkillResponse
    response_at_3: CharacterSkillResponse
    response_at_4: CharacterSkillResponse
    response_at_hyper_passive: CharacterSkillResponse
    response_at_hyper_active: CharacterSkillResponse
    response_at_5: CharacterSkillResponse
    response_at_6: CharacterSkillResponse


class _HexaStatCore(TypedDict):
    slot_id: str
    main_stat_name: str
    sub_stat_name_1: str
    sub_stat_name_2: str
    main_stat_level: int
    sub_stat_level_1: int
    sub_stat_level_2: int
    stat_grade: int


class HexaStatResponse(TypedDict):
    date: str
    character_class: str
    character_hexa_stat_core: list[_HexaStatCore]  # always length 1
    character_hexa_stat_core_2: list[_HexaStatCore]  # always length 1
    preset_hexa_stat_core: list[_HexaStatCore]
    preset_hexa_stat_core_2: list[_HexaStatCore]


def get_hexamatrix_stat_response(
    host: str, access_token: str, payload: CharacterIDWithDate
) -> HexaStatResponse:
    return cast(
        HexaStatResponse,
        requests.get(
            f"{host}/maplestory/v1/character/hexamatrix-stat",
            headers=get_nexon_api_header(access_token),
            params=cast(dict, payload),
            allow_redirects=True,
        ).json(),
    )


class CharacterSkillPayLoad(TypedDict):
    ocid: str
    date: str
    character_skill_grade: str


def get_skill_response(
    host: str, access_token: str, payload: CharacterSkillPayLoad
) -> CharacterSkillResponse:
    return cast(
        CharacterSkillResponse,
        requests.get(
            f"{host}/maplestory/v1/character/skill",
            headers=get_nexon_api_header(access_token),
            params=cast(dict, payload),
            allow_redirects=True,
        ).json(),
    )


def get_every_skill_levels(
    host: str, access_token: str, payload: CharacterIDWithDate
) -> AggregatedCharacterSkillResponse:
    return {
        "response_at_0": get_skill_response(
            host,
            access_token,
            {
                "ocid": payload["ocid"],
                "date": payload["date"],
                "character_skill_grade": "0",
            },
        ),
        "response_at_1": get_skill_response(
            host,
            access_token,
            {
                "ocid": payload["ocid"],
                "date": payload["date"],
                "character_skill_grade": "1",
            },
        ),
        "response_at_1_and_half": get_skill_response(
            host,
            access_token,
            {
                "ocid": payload["ocid"],
                "date": payload["date"],
                "character_skill_grade": "1.5",
            },
        ),
        "response_at_2": get_skill_response(
            host,
            access_token,
            {
                "ocid": payload["ocid"],
                "date": payload["date"],
                "character_skill_grade": "2",
            },
        ),
        "response_at_2_and_half": get_skill_response(
            host,
            access_token,
            {
                "ocid": payload["ocid"],
                "date": payload["date"],
                "character_skill_grade": "2.5",
            },
        ),
        "response_at_3": get_skill_response(
            host,
            access_token,
            {
                "ocid": payload["ocid"],
                "date": payload["date"],
                "character_skill_grade": "3",
            },
        ),
        "response_at_4": get_skill_response(
            host,
            access_token,
            {
                "ocid": payload["ocid"],
                "date": payload["date"],
                "character_skill_grade": "4",
            },
        ),
        "response_at_hyper_passive": get_skill_response(
            host,
            access_token,
            {
                "ocid": payload["ocid"],
                "date": payload["date"],
                "character_skill_grade": "hyperpassive",
            },
        ),
        "response_at_hyper_active": get_skill_response(
            host,
            access_token,
            {
                "ocid": payload["ocid"],
                "date": payload["date"],
                "character_skill_grade": "hyperactive",
            },
        ),
        "response_at_5": get_skill_response(
            host,
            access_token,
            {
                "ocid": payload["ocid"],
                "date": payload["date"],
                "character_skill_grade": "5",
            },
        ),
        "response_at_6": get_skill_response(
            host,
            access_token,
            {
                "ocid": payload["ocid"],
                "date": payload["date"],
                "character_skill_grade": "6",
            },
        ),
    }
