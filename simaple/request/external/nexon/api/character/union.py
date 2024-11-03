from typing import TypedDict, cast

import requests

from simaple.request.external.nexon.api.character.common import (
    CharacterIDWithDate,
    get_nexon_api_header,
)


class CharacterUnionResponse(TypedDict):
    date: str
    union_level: int
    union_grade: str


class _CharacterUnionRaiderBlockPos(TypedDict):
    x: int
    y: int


class CharacterUnionRaiderBlock(TypedDict):
    block_type: str
    block_class: str
    block_level: str
    block_control_point: _CharacterUnionRaiderBlockPos
    block_position: list[_CharacterUnionRaiderBlockPos]


class UnionInnerStatRow(TypedDict):
    """Union 내부 배치 방식"""

    stat_field_id: int
    stat_field_effect: str


class CharacterUnionRaiderPreset(TypedDict):
    union_raider_stat: list[str]
    union_occupied_stat: list[str]
    union_block: list[CharacterUnionRaiderBlock]
    union_inner_stat: list[UnionInnerStatRow]


class CharacterUnionRaiderResponse(TypedDict):
    date: str
    union_raider_stat: list[str]
    union_occupied_stat: list[str]
    union_block: list[CharacterUnionRaiderBlock]
    union_inner_stat: list[UnionInnerStatRow]
    use_preset_no: int
    union_raider_preset_1: CharacterUnionRaiderPreset
    union_raider_preset_2: CharacterUnionRaiderPreset
    union_raider_preset_3: CharacterUnionRaiderPreset
    union_raider_preset_4: CharacterUnionRaiderPreset
    union_raider_preset_5: CharacterUnionRaiderPreset


def get_character_union_raider_response(
    host: str, access_token: str, payload: CharacterIDWithDate
) -> CharacterUnionRaiderResponse:
    return cast(
        CharacterUnionRaiderResponse,
        requests.get(
            f"{host}/maplestory/v1/user/union-raider",
            headers=get_nexon_api_header(access_token),
            params=cast(dict, payload),
        ).json(),
    )


class _UnionArtifactEffect(TypedDict):
    name: str
    level: int


class _UnionArtifactCrystal(TypedDict):
    name: str
    validity_flag: str
    date_expire: str
    level: int
    crystal_option_name_1: str
    crystal_option_name_2: str
    crystal_option_name_3: str


class UnionArtifactResponse(TypedDict):
    date: str
    union_artifact_effect: list[_UnionArtifactEffect]
    union_artifact_crystal: list[_UnionArtifactCrystal]
    union_artifact_remain_ap: int


def get_union_artifact_response(
    host: str, access_token: str, payload: CharacterIDWithDate
) -> UnionArtifactResponse:
    return cast(
        UnionArtifactResponse,
        requests.get(
            f"{host}/maplestory/v1/user/union-artifact",
            headers=get_nexon_api_header(access_token),
            params=cast(dict, payload),
        ).json(),
    )
