import os

import pytest
from fastapi.testclient import TestClient

from simaple.app.interface.handler import add_exception_handlers
from simaple.app.interface.web import SimapleWeb


@pytest.fixture
def simulator_configuration():
    return {
        "action_stat": {},
        "job": "archmagefb",
        "character_level": 260,
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
            "elemental_resistance": 10,
        },
    }


@pytest.fixture
def baseline_configuration():
    return {
        "simulation_setting": {
            "tier": "Legendary",
            "jobtype": "archmagefb",
            "job_category": 1,  # 0~4
            "level": 270,
            "passive_skill_level": 0,
            "combat_orders_level": 1,
            "v_skill_level": 30,
            "v_improvements_level": 60,
        }
    }


@pytest.fixture
def record_file_name():
    return os.path.join(os.path.dirname(__file__), "record.tsv")


@pytest.fixture
def client():
    app = SimapleWeb()
    add_exception_handlers(app)
    app.reset_database()
    app_client = TestClient(app)

    return app_client
