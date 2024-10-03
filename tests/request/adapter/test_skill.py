from simaple.request.adapter.skill_loader._converter import compute_passive_skill_stat


def test_passive_fetch(skill_aggregated_response):
    passive_stat = compute_passive_skill_stat(
        skill_aggregated_response, character_level=284
    )
    assert passive_stat.model_dump() == {
        "stat": {
            "STR": 0.0,
            "LUK": 0.0,
            "INT": 255.0,
            "DEX": 0.0,
            "STR_multiplier": 0.0,
            "LUK_multiplier": 0.0,
            "INT_multiplier": 0.0,
            "DEX_multiplier": 0.0,
            "STR_static": 0.0,
            "LUK_static": 0.0,
            "INT_static": 0.0,
            "DEX_static": 0.0,
            "attack_power": 20.0,
            "magic_attack": 63.0,
            "attack_power_multiplier": 0.0,
            "magic_attack_multiplier": 0.0,
            "critical_rate": 30.0,
            "critical_damage": 13.0,
            "boss_damage_multiplier": 0.0,
            "damage_multiplier": 50.0,
            "final_damage_multiplier": 40.0,
            "ignored_defence": 20.0,
            "MHP": 475.0,
            "MMP": 475.0,
            "MHP_multiplier": 0.0,
            "MMP_multiplier": 0.0,
            "elemental_resistance": 10.0,
        },
        "action_stat": {
            "cooltime_reduce": 0.0,
            "summon_duration": 0.0,
            "buff_duration": 55.0,
            "cooltime_reduce_rate": 0.0,
        },
        "level_stat": {
            "STR": 0.0,
            "LUK": 0.0,
            "INT": 0.0,
            "DEX": 0.0,
            "attack_power": 0.0,
            "magic_attack": 0.0,
        },
    }
