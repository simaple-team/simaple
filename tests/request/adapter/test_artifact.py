from simaple.core import ExtendedStat
from simaple.request.adapter.union_loader import _get_union_artifact


def test_propensity_response(union_artifact_response):
    artifact = _get_union_artifact(union_artifact_response)
    assert artifact.get_extended_stat() == ExtendedStat.model_validate(
        {
            "stat": {
                "INT": 150,
                "STR": 150,
                "DEX": 150,
                "LUK": 150,
                "attack_power": 30,
                "magic_attack": 30,
                "critical_rate": 20,
                "damage_multiplier": 15,
                "boss_damage_multiplier": 15,
                "critical_damage": 4,
                "ignored_defence": 20,
            },
            "action_stat": {"buff_duration": 20},
        }
    )
