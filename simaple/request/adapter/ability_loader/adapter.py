import datetime

from simaple.core import ExtendedStat
from simaple.request.adapter.ability_loader._converter import (
    get_ability_stat_from_ability_text,
)
from simaple.request.external.nexon.api.character.ability import (
    _CharacterAbilityLineResponse,
    get_character_ability,
)
from simaple.request.external.nexon.api.ocid import (
    as_nexon_datetime,
    get_character_ocid,
)
from simaple.request.external.nexon.client import NexonAPIClient
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
    def __init__(self, client: NexonAPIClient):
        self._client = client

    def load_stat(self, character_name: str) -> ExtendedStat:
        ability_response = self._client.session(character_name).request(
            get_character_ability
        )
        return _get_ability_stat(ability_response["ability_info"])

    def load_best_stat(
        self, character_name: str, selector: BestStatSelector
    ) -> ExtendedStat:
        ability_response = self._client.session(character_name).request(
            get_character_ability
        )
        candidates = [
            _get_ability_stat(ability_response["ability_preset_1"]["ability_info"]),
            _get_ability_stat(ability_response["ability_preset_2"]["ability_info"]),
            _get_ability_stat(ability_response["ability_preset_3"]["ability_info"]),
        ]
        best_candidate_index = get_best_stat_index(candidates, selector)
        return candidates[best_candidate_index]
