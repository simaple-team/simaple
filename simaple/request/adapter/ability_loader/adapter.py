import datetime

from simaple.core import ExtendedStat
from simaple.request.adapter.ability_loader._converter import (
    get_ability_stat_from_ability_text,
)
from simaple.request.external.nexon.api.character import (
    as_nexon_datetime,
    get_character_ability,
    get_character_ocid,
)
from simaple.request.external.nexon.schema.character.ability import (
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
    def __init__(self, host: str, access_token: str, date: datetime.date):
        self._host = host
        self._access_token = access_token
        self._date = date

    def load_stat(self, character_name: str, date: datetime.date) -> ExtendedStat:
        ocid = get_character_ocid(self._host, self._access_token, character_name)
        ability_response = get_character_ability(
            self._host,
            self._access_token,
            {"ocid": ocid, "date": as_nexon_datetime(self._date)},
        )
        return _get_ability_stat(ability_response["ability_info"])

    def load_best_stat(
        self, character_name: str, selector: BestStatSelector
    ) -> ExtendedStat:
        ocid = get_character_ocid(self._host, self._access_token, character_name)
        ability_response = get_character_ability(
            self._host,
            self._access_token,
            {"ocid": ocid, "date": as_nexon_datetime(self._date)},
        )

        candidates = [
            _get_ability_stat(ability_response["ability_preset_1"]["ability_info"]),
            _get_ability_stat(ability_response["ability_preset_2"]["ability_info"]),
            _get_ability_stat(ability_response["ability_preset_3"]["ability_info"]),
        ]
        best_candidate_index = get_best_stat_index(candidates, selector)
        return candidates[best_candidate_index]
