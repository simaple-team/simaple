import datetime

from simaple.core import JobType, Stat
from simaple.request.adapter.translator.job_name import translate_kms_name
from simaple.request.external.nexon.api.character import (
    as_nexon_datetime,
    get_character_basic,
    get_character_ocid,
    get_character_stat,
)
from simaple.request.external.nexon.schema.character.basic import CharacterStatResponse
from simaple.request.service.loader import CharacterBasicLoader


class NexonAPICharacterBasicLoader(CharacterBasicLoader):
    def __init__(self, host: str, access_token: str, date: datetime.date):
        self._host = host
        self._access_token = access_token
        self._date = date

    def load_character_level(self, character_name: str) -> int:
        ocid = get_character_ocid(self._host, self._access_token, character_name)
        character_basic_response = get_character_basic(
            self._host,
            self._access_token,
            {"ocid": ocid, "date": as_nexon_datetime(self._date)},
        )
        return character_basic_response["character_level"]

    def load_character_ap_based_stat(self, character_name: str) -> Stat:
        ocid = get_character_ocid(self._host, self._access_token, character_name)
        character_stat_response = get_character_stat(
            self._host,
            self._access_token,
            {"ocid": ocid, "date": as_nexon_datetime(self._date)},
        )
        return extract_character_ap_based_stat(character_stat_response)

    def load_character_job_type(self, character_name: str) -> JobType:
        ocid = get_character_ocid(self._host, self._access_token, character_name)
        character_basic_response = get_character_basic(
            self._host,
            self._access_token,
            {"ocid": ocid, "date": as_nexon_datetime(self._date)},
        )
        return translate_kms_name(character_basic_response["character_class"])


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
