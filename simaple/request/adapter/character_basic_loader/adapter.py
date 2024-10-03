from typing import cast

from simaple.core import Stat
from simaple.request.adapter.character_basic_loader._schema import (
    CharacterBasicResponse,
    CharacterStatResponse,
)
from simaple.request.adapter.nexon_api import (
    HOST,
    Token,
    get_character_id,
    get_character_id_param,
)
from simaple.request.service.loader import CharacterBasicLoader


class NexonAPICharacterBasicLoader(CharacterBasicLoader):
    def __init__(self, token_value: str):
        self._token = Token(token_value)

    def load_character_level(self, character_name: str) -> int:
        character_id = get_character_id(self._token, character_name)
        uri = f"{HOST}/maplestory/v1/character/basic"
        resp = cast(
            CharacterBasicResponse,
            self._token.request(uri, get_character_id_param(character_id)),
        )
        return resp["character_level"]

    def load_character_ap_based_stat(self, character_name: str) -> Stat:
        character_id = get_character_id(self._token, character_name)
        uri = f"{HOST}/maplestory/v1/character/stat"
        resp = cast(
            CharacterStatResponse,
            self._token.request(uri, get_character_id_param(character_id)),
        )
        return extract_character_ap_based_stat(resp)


def extract_character_ap_based_stat(response: CharacterStatResponse) -> Stat:
    stat_names_and_mapping = {
        "AP 배분 STR": "STR",
        "AP 배분 DEX": "DEX",
        "AP 배분 INT": "INT",
        "AP 배분 LUK": "LUK",
        "AP 배분 HP": "MHP",
        "AP 배분 MP": "MMP",
    }

    stat = Stat()
    for final_stat in response["final_stat"]:
        if final_stat["stat_name"] in stat_names_and_mapping:
            stat += Stat.model_validate(
                {
                    stat_names_and_mapping[final_stat["stat_name"]]: int(
                        final_stat["stat_value"]
                    )
                }
            )

    return stat
