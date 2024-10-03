from simaple.core import ExtendedStat
from simaple.request.adapter.ability_loader.adapter import _get_ability_stat


def test_ability_response(character_ability_response):
    ability = _get_ability_stat(character_ability_response["ability_info"])

    assert ability == ExtendedStat.model_validate(
        {
            "stat": {
                "critical_rate": 20,
                "boss_damage_multiplier": 8,
            },
            "action_stat": {"buff_duration": 50},
        }
    )


def test_noisy_ability_response(character_ability_response_2):
    ability = _get_ability_stat(character_ability_response_2["ability_info"])

    assert ability == ExtendedStat.model_validate(
        {
            "stat": {"LUK_static": 9, "INT_static": 36},
            "action_stat": {"buff_duration": 45},
        }
    )
