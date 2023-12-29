from typing import Any, cast

from simaple.request.application.base import (
    HOST,
    CharacterID,
    Token,
    get_character_id_param,
)
from simaple.request.schema.character import (
    CharacterHyperStat,
    CharacterPopularity,
    CharacterPropensity,
    CharacterUnion,
    CharacterUnionRaider,
    CharacterUnionRaiderBlock,
)


async def get_character_hyper_stat(
    token: Token, character_id: CharacterID
) -> CharacterHyperStat:
    uri = f"{HOST}/maplestory/v1/character/hyper-stat"
    resp = await token.request(uri, get_character_id_param(character_id))

    return {
        "date": resp["date"],
        "character_class": resp["character_class"],
        "use_preset_no": int(resp["use_preset_no"]),
        "use_available_hyper_stat": resp["use_available_hyper_stat"],
        "hyper_stat_preset_1": resp["hyper_stat_preset_1"],
        "hyper_stat_preset_1_remain_point": resp["hyper_stat_preset_1_remain_point"],
        "hyper_stat_preset_2": resp["hyper_stat_preset_2"],
        "hyper_stat_preset_2_remain_point": resp["hyper_stat_preset_2_remain_point"],
        "hyper_stat_preset_3": resp["hyper_stat_preset_3"],
        "hyper_stat_preset_3_remain_point": resp["hyper_stat_preset_3_remain_point"],
    }


async def get_character_popularity(
    token: Token, character_id: CharacterID
) -> CharacterPopularity:
    uri = f"{HOST}/maplestory/v1/character/popularity"
    resp = await token.request(uri, get_character_id_param(character_id))

    return {
        "date": resp["date"],
        "popularity": resp["popularity"],
    }


async def get_character_propensity(
    token: Token, character_id: CharacterID
) -> CharacterPropensity:
    uri = f"{HOST}/maplestory/v1/character/propensity"
    resp = await token.request(uri, get_character_id_param(character_id))

    return cast(CharacterPropensity, resp)


async def get_character_union(
    token: Token, character_id: CharacterID
) -> CharacterUnion:
    uri = f"{HOST}/maplestory/v1/user/union"
    resp = await token.request(uri, get_character_id_param(character_id))

    return cast(CharacterUnion, resp)


def _get_union_block(raw: dict[str, Any]) -> CharacterUnionRaiderBlock:
    return {
        "block_type": raw["block_type"],
        "block_class": raw["block_class"],
        "block_level": int(raw["block_level"]),
        "block_control_point": raw["block_control_point"],
        "block_position": raw["block_position"],
    }


async def get_character_union_raiders(
    token: Token, character_id: CharacterID
) -> CharacterUnionRaider:
    uri = f"{HOST}/maplestory/v1/user/union-raider"
    resp = await token.request(uri, get_character_id_param(character_id))

    return {
        "date": resp["date"],
        "union_raider_stat": resp["union_raider_stat"],
        "union_occupied_stat": resp["union_occupied_stat"],
        "union_block": [_get_union_block(raw) for raw in resp["union_block"]],
        "union_inner_stat": [
            {
                "stat_field_id": int(raw["stat_field_id"]),
                "stat_field_effect": raw["stat_field_effect"],
            }
            for raw in resp["union_inner_stat"]
        ],
    }
