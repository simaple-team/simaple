import datetime

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
from simaple.request.external.nexon.api.ocid import (
    as_nexon_datetime,
    get_character_ocid,
)
from simaple.request.service.loader import CharacterSkillLoader
from simaple.system.hexa_stat import HexaStat


class NexonAPICharacterSkillLoader(CharacterSkillLoader):
    def __init__(self, host: str, access_token: str, date: datetime.date):
        self._host = host
        self._access_token = access_token
        self._date = date

    def load_character_passive_stat(
        self, character_name: str, character_level: int
    ) -> ExtendedStat:
        ocid = get_character_ocid(self._host, self._access_token, character_name)
        aggregated_response = get_every_skill_levels(
            self._host,
            self._access_token,
            {"ocid": ocid, "date": as_nexon_datetime(self._date)},
        )
        return compute_passive_skill_stat(aggregated_response, character_level)

    def load_character_hexa_stat(
        self,
        character_name: str,
    ) -> HexaStat:
        ocid = get_character_ocid(self._host, self._access_token, character_name)
        response = get_hexamatrix_stat_response(
            self._host,
            self._access_token,
            {"ocid": ocid, "date": as_nexon_datetime(self._date)},
        )
        return compute_hexa_stat(response)

    def load_zero_grade_skill_passive_stat(
        self, character_name: str
    ) -> tuple[ExtendedStat, bool]:
        ocid = get_character_ocid(self._host, self._access_token, character_name)
        response = get_skill_response(
            self._host,
            self._access_token,
            {
                "ocid": ocid,
                "date": as_nexon_datetime(self._date),
                "character_skill_grade": "0",
            },
        )
        return get_zero_order_skill_effect(response)

    def load_hexa_skill_levels(
        self, character_name: str
    ) -> tuple[dict[str, int], dict[str, int]]:
        """
        헥사스킬 레벨을 반환합니다.
        """
        ocid = get_character_ocid(self._host, self._access_token, character_name)
        response = get_skill_response(
            self._host,
            self._access_token,
            {
                "ocid": ocid,
                "date": as_nexon_datetime(self._date),
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
            skill_info["skill_name"]
            .replace("강화", "")
            .strip(): skill_info["skill_level"]
            for skill_info in response["character_skill"]
            if "강화" in skill_info["skill_name"]
        }
        return hexa_skill_levels, hexa_improvement_levels
