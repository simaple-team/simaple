from simaple.request.application.base import (
    HOST,
    CharacterID,
    Token,
    get_character_id_param,
)
from simaple.request.schema.character import CharacterHyperStat


async def get_hyperstat(token: Token, character_id: CharacterID) -> CharacterHyperStat:
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
