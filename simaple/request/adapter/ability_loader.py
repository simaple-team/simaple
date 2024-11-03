import re

from loguru import logger

from simaple.core import ActionStat, ExtendedStat, Stat
from simaple.request.external.nexon.api.character.ability import (
    _CharacterAbilityLineResponse,
    get_character_ability,
)
from simaple.request.external.nexon.client import NexonAPIClient
from simaple.request.service.loader import AbilityLoader
from simaple.request.service.util import BestStatSelector, get_best_stat_index


def single_valued_text_to_stat(text: str) -> ExtendedStat | None:
    pattern = re.compile(r"([A-Z/가-힣a-z\s]+)([\d\.]+)(%)? 증가")
    match = pattern.search(text)
    if not match:
        return None

    option_name, option_value = match.group(1).strip(), int(match.group(2))

    match option_name:
        case "버프 스킬의 지속 시간":
            return ExtendedStat(action_stat=ActionStat(buff_duration=option_value))
        case "보스 몬스터 공격 시 데미지":
            return ExtendedStat(stat=Stat(boss_damage_multiplier=option_value))
        case "크리티컬 확률":
            return ExtendedStat(stat=Stat(critical_rate=option_value))
        case "INT":
            return ExtendedStat(stat=Stat(INT_static=option_value))
        case "LUK":
            return ExtendedStat(stat=Stat(LUK_static=option_value))
        case "STR":
            return ExtendedStat(stat=Stat(STR_static=option_value))
        case "DEX":
            return ExtendedStat(stat=Stat(DEX_static=option_value))
        case "공격력":
            return ExtendedStat(stat=Stat(attack_power=option_value))
        case "마력":
            return ExtendedStat(stat=Stat(magic_attack=option_value))
        case "모든 능력치":
            return ExtendedStat(
                stat=Stat(
                    STR_static=option_value,
                    DEX_static=option_value,
                    INT_static=option_value,
                    LUK_static=option_value,
                )
            )
        case "아이템 드롭률":
            return ExtendedStat()
        case "메소 획득량":
            return ExtendedStat()

    return ExtendedStat()


def double_valued_text_to_stat(text: str) -> ExtendedStat | None:
    pattern = re.compile(
        r"([A-Z/가-힣a-z\s]+) ([0-9]+) 증가, ([A-Z/가-힣a-z\s]+) ([0-9]+) 증가"
    )
    match = pattern.search(text)
    if not match:
        return None

    first_option_name, first_option_value = match.group(1).strip(), int(match.group(2))
    second_option_name, second_option_value = (
        match.group(3).strip(),
        int(match.group(4)),
    )

    print(
        f"first_option_name: {first_option_name}, first_option_value: {first_option_value}, second_option_name: {second_option_name}, second_option_value: {second_option_value}"
    )
    return ExtendedStat(
        stat=Stat.model_validate(
            {
                f"{first_option_name}_static": first_option_value,
                f"{second_option_name}_static": second_option_value,
            }
        )
    )


def ability_text_to_stat(text: str) -> ExtendedStat:
    double_valued_stat = double_valued_text_to_stat(text)
    if double_valued_stat is not None:
        return double_valued_stat

    single_valued_stat = single_valued_text_to_stat(text)
    if single_valued_stat is not None:
        return single_valued_stat

    logger.warning(f"Invalid occupation description: {text}")
    return ExtendedStat()


def get_ability_stat(
    ability_line_infos: list[_CharacterAbilityLineResponse],
) -> ExtendedStat:
    ability_stat = ExtendedStat()
    for ability_line_info in ability_line_infos:
        ability_stat += ability_text_to_stat(ability_line_info["ability_value"])

    return ability_stat


class NexonAPIAbilityLoader(AbilityLoader):
    def __init__(self, client: NexonAPIClient):
        self._client = client

    def load_stat(self, character_name: str) -> ExtendedStat:
        ability_response = self._client.session(character_name).request(
            get_character_ability
        )
        return get_ability_stat(ability_response["ability_info"])

    def load_best_stat(
        self, character_name: str, selector: BestStatSelector
    ) -> ExtendedStat:
        ability_response = self._client.session(character_name).request(
            get_character_ability
        )
        candidates = [
            get_ability_stat(ability_response["ability_preset_1"]["ability_info"]),
            get_ability_stat(ability_response["ability_preset_2"]["ability_info"]),
            get_ability_stat(ability_response["ability_preset_3"]["ability_info"]),
        ]
        best_candidate_index = get_best_stat_index(candidates, selector)
        return candidates[best_candidate_index]
