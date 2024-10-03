from typing import cast

from simaple.core import ExtendedStat, Stat
from simaple.data.system.hexa_stat import get_all_hexa_stat_cores
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
from simaple.request.adapter.skill_loader._converter import (
    compute_hexa_stat,
    compute_passive_skill_stat,
    get_zero_order_skill_effect,
)
from simaple.request.adapter.skill_loader._schema import (
    AggregatedCharacterSkillResponse,
    CharacterSkillResponse,
    HexaStatResponse,
)
from simaple.request.service.loader import CharacterSkillLoader
from simaple.system.hexa_stat import HexaStat, HexaStatCore


class NexonAPICharacterSkillLoader(CharacterSkillLoader):
    def __init__(self, token_value: str):
        self._token = Token(token_value)

    def load_character_passive_stat(
        self, character_name: str, character_level: int
    ) -> ExtendedStat:
        aggregated_response = self._get_aggregated_response(character_name)
        return compute_passive_skill_stat(aggregated_response, character_level)

    def load_character_hexa_stat(
        self,
        character_name: str,
    ) -> HexaStat:
        uri = f"{HOST}/maplestory/v1/character/hexamatrix-stat"
        character_id = get_character_id(self._token, character_name)
        response = cast(
            HexaStatResponse,
            self._token.request(uri, get_character_id_param(character_id)),
        )
        return compute_hexa_stat(response)

    def load_zero_grade_skill_passive_stat(
        self, character_name: str
    ) -> tuple[ExtendedStat, bool]:
        uri = f"{HOST}/maplestory/v1/character/skill"
        response = cast(
            CharacterSkillResponse,
            self._token.request(uri, self._get_query_param(character_name, "0")),
        )
        return get_zero_order_skill_effect(response)

    def _get_query_param(self, character_name: str, skill_order: str) -> dict:
        character_id = get_character_id(self._token, character_name)
        return {
            "character_skill_grade": skill_order,
            **get_character_id_param(character_id),
        }

    def _get_aggregated_response(
        self, character_name: str
    ) -> AggregatedCharacterSkillResponse:

        uri = f"{HOST}/maplestory/v1/character/skill"
        return {
            "response_at_0": cast(
                CharacterSkillResponse,
                self._token.request(uri, self._get_query_param(character_name, "0")),
            ),
            "response_at_1": cast(
                CharacterSkillResponse,
                self._token.request(uri, self._get_query_param(character_name, "0")),
            ),
            "response_at_1_and_half": cast(
                CharacterSkillResponse,
                self._token.request(uri, self._get_query_param(character_name, "1.5")),
            ),
            "response_at_2": cast(
                CharacterSkillResponse,
                self._token.request(uri, self._get_query_param(character_name, "2")),
            ),
            "response_at_2_and_half": cast(
                CharacterSkillResponse,
                self._token.request(uri, self._get_query_param(character_name, "2.5")),
            ),
            "response_at_3": cast(
                CharacterSkillResponse,
                self._token.request(uri, self._get_query_param(character_name, "3")),
            ),
            "response_at_4": cast(
                CharacterSkillResponse,
                self._token.request(uri, self._get_query_param(character_name, "4")),
            ),
            "response_at_hyper_passive": cast(
                CharacterSkillResponse,
                self._token.request(
                    uri, self._get_query_param(character_name, "hyperpassive")
                ),
            ),
            "response_at_hyper_active": cast(
                CharacterSkillResponse,
                self._token.request(
                    uri, self._get_query_param(character_name, "hyperactive")
                ),
            ),
            "response_at_5": cast(
                CharacterSkillResponse,
                self._token.request(uri, self._get_query_param(character_name, "5")),
            ),
            "response_at_6": cast(
                CharacterSkillResponse,
                self._token.request(uri, self._get_query_param(character_name, "6")),
            ),
        }
