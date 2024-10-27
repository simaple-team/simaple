from typing import cast

from simaple.core import ExtendedStat
from simaple.request.adapter.ability_loader._converter import (
    get_ability_stat_from_ability_text,
)
from simaple.request.external.nexon.api.auth import (
    HOST,
    Token,
    get_character_id,
    get_character_id_param,
)
from simaple.request.external.nexon.schema.character.ability import (
    CharacterAbilityResponse,
    _CharacterAbilityLineResponse,
)
from simaple.request.service.loader import AbilityLoader
from simaple.request.service.util import BestStatSelector, get_best_stat_index


def _get_ability_stat(
    ability_line_infos: list[_CharacterAbilityLineResponse],
) -> ExtendedStat:
    ability_stat = ExtendedStat()
    for ability_line_info in ability_line_infos:
        ability_stat += get_ability_stat_from_ability_text(
            ability_line_info["ability_value"]
        )

    return ability_stat


class NexonAPIAbilityLoader(AbilityLoader):
    def __init__(self, token_value: str):
        self._token = Token(token_value)

    def load_stat(self, character_name: str) -> ExtendedStat:
        character_id = get_character_id(self._token, character_name)
        uri = f"{HOST}/maplestory/v1/character/ability"
        resp = cast(
            CharacterAbilityResponse,
            self._token.request(uri, get_character_id_param(character_id)),
        )
        return _get_ability_stat(resp["ability_info"])

    def load_best_stat(
        self, character_name: str, selector: BestStatSelector
    ) -> ExtendedStat:
        character_id = get_character_id(self._token, character_name)
        uri = f"{HOST}/maplestory/v1/character/ability"
        resp = cast(
            CharacterAbilityResponse,
            self._token.request(uri, get_character_id_param(character_id)),
        )

        candidates = [
            _get_ability_stat(resp["ability_preset_1"]["ability_info"]),
            _get_ability_stat(resp["ability_preset_2"]["ability_info"]),
            _get_ability_stat(resp["ability_preset_3"]["ability_info"]),
        ]
        best_candidate_index = get_best_stat_index(candidates, selector)
        return candidates[best_candidate_index]
