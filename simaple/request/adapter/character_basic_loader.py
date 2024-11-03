from simaple.core import JobType, Stat
from simaple.core.jobtype import translate_kms_name
from simaple.request.external.nexon.api.character.basic import (
    CharacterStatResponse,
    get_character_basic,
    get_character_stat,
)
from simaple.request.external.nexon.client import NexonAPIClient
from simaple.request.service.loader import CharacterBasicLoader


class NexonAPICharacterBasicLoader(CharacterBasicLoader):
    def __init__(self, client: NexonAPIClient):
        self._client = client

    def load_character_level(self, character_name: str) -> int:
        character_basic_response = self._client.session(character_name).request(
            get_character_basic
        )
        return character_basic_response["character_level"]

    def load_character_ap_based_stat(self, character_name: str) -> Stat:
        character_stat_response = self._client.session(character_name).request(
            get_character_stat
        )
        return extract_character_ap_based_stat(character_stat_response)

    def load_character_job_type(self, character_name: str) -> JobType:
        character_basic_response = self._client.session(character_name).request(
            get_character_basic
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
