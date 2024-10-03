from typing import cast

from simaple.core import ExtendedStat
from simaple.request.adapter.ability_loader._converter import (
    get_ability_stat_from_ability_text,
)
from simaple.request.adapter.ability_loader._schema import CharacterAbilityResponse
from simaple.request.adapter.nexon_api import (
    HOST,
    Token,
    get_character_id,
    get_character_id_param,
)
from simaple.request.service.loader import AbilityLoader


def _get_ability_stat(response: CharacterAbilityResponse) -> ExtendedStat:
    ability_stat = ExtendedStat()
    for ability_line_info in response["ability_info"]:
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
        return _get_ability_stat(resp)
