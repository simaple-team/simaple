from simaple.core import ExtendedStat
from simaple.request.adapter.skill_loader._converter import (
    compute_hexa_stat,
    compute_passive_skill_stat,
    get_zero_order_skill_effect,
)
from simaple.request.external.nexon.api.character.skill import (
    get_every_skill_levels,
    get_hexamatrix_stat_response,
    get_skill_response,
)
from simaple.request.external.nexon.client import NexonAPIClient
from simaple.request.service.loader import CharacterSkillLoader
from simaple.system.hexa_stat import HexaStat


class NexonAPICharacterSkillLoader(CharacterSkillLoader):
    def __init__(self, client: NexonAPIClient):
        self._client = client

    def load_character_passive_stat(
        self, character_name: str, character_level: int
    ) -> ExtendedStat:
        aggregated_response = self._client.session(character_name).request(
            get_every_skill_levels
        )
        return compute_passive_skill_stat(aggregated_response, character_level)

    def load_character_hexa_stat(
        self,
        character_name: str,
    ) -> HexaStat:
        response = self._client.session(character_name).request(
            get_hexamatrix_stat_response
        )

        return compute_hexa_stat(response)

    def load_zero_grade_skill_passive_stat(
        self, character_name: str
    ) -> tuple[ExtendedStat, bool]:
        response = self._client.session(character_name).request(
            get_skill_response,
            {
                "character_skill_grade": "0",
            },
        )
        return get_zero_order_skill_effect(response)

    def load_combat_power_related_stat(
        self,
        character_name: str,
    ) -> tuple[ExtendedStat, bool]:
        response = self._client.session(character_name).request(
            get_skill_response,
            {
                "character_skill_grade": "0",
            },
        )
        return get_zero_order_skill_effect(response, ["연합의 의지"])

    def load_hexa_skill_levels(
        self, character_name: str
    ) -> tuple[dict[str, int], dict[str, int]]:
        """
        헥사스킬 레벨을 반환합니다.
        """
        response = self._client.session(character_name).request(
            get_skill_response,
            {
                "character_skill_grade": "6",
            },
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
            skill_info["skill_name"].replace("강화", "").strip(): skill_info[
                "skill_level"
            ]
            for skill_info in response["character_skill"]
            if "강화" in skill_info["skill_name"]
        }
        return hexa_skill_levels, hexa_improvement_levels
