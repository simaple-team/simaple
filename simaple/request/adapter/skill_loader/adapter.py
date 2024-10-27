from typing import cast

from simaple.core import ExtendedStat
from simaple.request.adapter.skill_loader._converter import (
    compute_hexa_stat,
    compute_passive_skill_stat,
    get_zero_order_skill_effect,
)
from simaple.request.external.nexon.api.auth import (
    HOST,
    Token,
    get_character_id,
    get_character_id_param,
)
from simaple.request.external.nexon.schema.character.skill import (
    AggregatedCharacterSkillResponse,
    CharacterSkillResponse,
    HexaStatResponse,
)
from simaple.request.service.loader import CharacterSkillLoader
from simaple.system.hexa_stat import HexaStat


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

    def load_hexa_skill_levels(
        self, character_name: str
    ) -> tuple[dict[str, int], dict[str, int]]:
        """
        헥사스킬 레벨을 반환합니다.
        """
        uri = f"{HOST}/maplestory/v1/character/skill"
        response = cast(
            CharacterSkillResponse,
            self._token.request(uri, self._get_query_param(character_name, "6")),
        )
        hexa_skill_levels = {
            skill_info["skill_name"]: skill_info["skill_level"]
            for skill_info in response["character_skill"]
            if "강화" not in skill_info["skill_name"]
            and skill_info["skill_name"]
            not in {
                "HEXA 스텟",
                "솔 야누스 : 새벽",
                "솔 야누스 : 황혼",
                "솔 야누스",
                "HEXA 스탯",
            }
        }
        hexa_improvement_levels = {
            skill_info["skill_name"]
            .replace("강화", "")
            .strip(): skill_info["skill_level"]
            for skill_info in response["character_skill"]
            if "강화" in skill_info["skill_name"]
        }
        return hexa_skill_levels, hexa_improvement_levels

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
