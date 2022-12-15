import os

import pytest


@pytest.fixture
def workspace_configuration():
    return {
        "action_stat": {},
        "groups": ["archmagefb", "common", "adventurer.magician"],
        "injected_values": {"character_level": 260},
        "skill_levels": {},
        "v_improvements": {},
        "character_stat": {
            "STR": 907.0,
            "LUK": 2224.0,
            "INT": 4932.0,
            "DEX": 832.0,
            "STR_multiplier": 86.0,
            "LUK_multiplier": 86.0,
            "INT_multiplier": 573.0,
            "DEX_multiplier": 86.0,
            "STR_static": 420.0,
            "LUK_static": 500.0,
            "INT_static": 15460.0,
            "DEX_static": 200.0,
            "attack_power": 1200.0,
            "magic_attack": 2075.0,
            "attack_power_multiplier": 0.0,
            "magic_attack_multiplier": 81.0,
            "critical_rate": 100.0,
            "critical_damage": 83.0,
            "boss_damage_multiplier": 144.0,
            "damage_multiplier": 167.7,
            "final_damage_multiplier": 110.0,
            "ignored_defence": 94.72006176400876,
            "MHP": 23105.0,
            "MMP": 12705.0,
            "MHP_multiplier": 0.0,
            "MMP_multiplier": 0.0,
        },
    }


@pytest.fixture
def record_file_name():
    return os.path.join(os.path.dirname(__file__), "record.tsv")
