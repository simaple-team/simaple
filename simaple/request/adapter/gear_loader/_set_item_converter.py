import re

from simaple.core import Stat
from simaple.request.external.nexon.api.character.item import SetEffectResponse


def _parse_each_option(option_string: str) -> Stat:
    if ":" not in option_string:
        return Stat()

    pattern = re.compile(r"([a-zA-Z가-힣\s]+) : \+(\d+)(%?)")
    match = pattern.search(option_string)
    if not match:
        return Stat()

    option_name = match.group(1)
    option_value = int(match.group(2))
    is_percentage = match.group(3) == "%"

    match (option_name, is_percentage):
        case ("최대 HP", False):
            return Stat(MHP=option_value)
        case ("최대 MP", False):
            return Stat(MMP=option_value)
        case ("최대 HP", True):
            return Stat(MHP_multiplier=option_value)
        case ("최대 MP", True):
            return Stat(MMP_multiplier=option_value)
        case ("공격력", False):
            return Stat(attack_power=option_value)
        case ("마력", False):
            return Stat(magic_attack=option_value)
        case ("올스탯", False):
            return Stat(
                STR=option_value, DEX=option_value, INT=option_value, LUK=option_value
            )
        case ("공격력", True):
            return Stat(attack_power_multiplier=option_value)
        case ("마력", True):
            return Stat(magic_attack_multiplier=option_value)
        case ("올스탯", True):
            return Stat.all_stat_multiplier(option_value)
        case ("몬스터 방어율 무시", True):
            return Stat(ignored_defence=option_value)
        case ("보스 몬스터 공격 시 데미지", True):
            return Stat(boss_damage_multiplier=option_value)
        case ("STR", False):
            return Stat(STR=option_value)
        case ("DEX", False):
            return Stat(DEX=option_value)
        case ("INT", False):
            return Stat(INT=option_value)
        case ("LUK", False):
            return Stat(LUK=option_value)
        case ("크리티컬 데미지", True):
            return Stat(critical_damage=option_value)
        case _:
            return Stat()


def parse_set_option_text_into_stat(value_string: str):
    each_options = value_string.split(", ")
    stat = Stat()

    for option in each_options:
        stat += _parse_each_option(option)

    return stat


def get_set_item_stats(response: SetEffectResponse):
    set_item_stat = Stat()

    for effect in response["set_effect"]:
        for set_option in effect["set_effect_info"]:
            stat = parse_set_option_text_into_stat(set_option["set_option"])
            set_item_stat += stat

    return set_item_stat
