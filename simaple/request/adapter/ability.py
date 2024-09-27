from simaple.core import ExtendedStat
from simaple.request.schema.character import CharacterAbility
from simaple.request.translator.ability import get_ability_stat_from_ability_text
from simaple.system.ability import AbilityLine, AbilityType


def get_ability_stat(character_ability_response: CharacterAbility) -> ExtendedStat:
    ability_stat = ExtendedStat()
    for ability_line_info in character_ability_response["ability_info"]:
        ability_stat += get_ability_stat_from_ability_text(
            ability_line_info["ability_value"]
        )

    return ability_stat
