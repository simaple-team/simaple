from typing import cast

from simaple.core import ExtendedStat, Stat
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
from simaple.request.adapter.skill_loader._converter import compute_passive_skill_stat
from simaple.request.adapter.skill_loader._schema import (
    AggregatedCharacterSkillResponse,
    CharacterSkillResponse,
)
from simaple.request.service.loader import CharacterSkillLoader


class NexonAPICharacterSkillLoader(CharacterSkillLoader):
    def __init__(self, token_value: str):
        self._token = Token(token_value)

    def load_character_passive_stat(self, character_name: str, character_level: int) -> ExtendedStat:
        aggregated_response = self._get_aggregated_response(character_name)
        return compute_passive_skill_stat(aggregated_response, character_level)

    def _get_aggregated_response(
        self, character_name: str
    ) -> AggregatedCharacterSkillResponse:
        def _get_query_param(skill_order: str) -> dict:
            character_id = get_character_id(self._token, character_name)
            return {
                "character_skill_grade": skill_order,
                **get_character_id_param(character_id),
            }

        uri = f"{HOST}/maplestory/v1/character/skill"
        return {
            "response_at_0": cast(
                CharacterSkillResponse,
                self._token.request(uri, _get_query_param("0")),
            ),
            "response_at_1": cast(
                CharacterSkillResponse,
                self._token.request(uri, _get_query_param("0")),
            ),
            "response_at_1_and_half": cast(
                CharacterSkillResponse,
                self._token.request(uri, _get_query_param("1.5")),
            ),
            "response_at_2": cast(
                CharacterSkillResponse,
                self._token.request(uri, _get_query_param("2")),
            ),
            "response_at_2_and_half": cast(
                CharacterSkillResponse,
                self._token.request(uri, _get_query_param("2.5")),
            ),
            "response_at_3": cast(
                CharacterSkillResponse,
                self._token.request(uri, _get_query_param("3")),
            ),
            "response_at_4": cast(
                CharacterSkillResponse,
                self._token.request(uri, _get_query_param("4")),
            ),
            "response_at_hyper_passive": cast(
                CharacterSkillResponse,
                self._token.request(uri, _get_query_param("hyperpassive")),
            ),
            "response_at_hyper_active": cast(
                CharacterSkillResponse,
                self._token.request(uri, _get_query_param("hyperactive")),
            ),
            "response_at_5": cast(
                CharacterSkillResponse,
                self._token.request(uri, _get_query_param("5")),
            ),
            "response_at_6": cast(
                CharacterSkillResponse,
                self._token.request(uri, _get_query_param("6")),
            ),
        }
