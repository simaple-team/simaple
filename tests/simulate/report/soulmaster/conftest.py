# pylint: disable=W0621
import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
import simaple.simulate.component.specific  # pylint: disable=W0611
from simaple.core.base import ActionStat, Stat
from simaple.simulate.kms import get_client


@pytest.fixture
def soulmaster_client():
    return get_client(
        ActionStat(),
        ["soulmaster", "common", "cygnus", "warrior"],
        {
            "character_level": 260,
            "weapon_pure_attack_power": 500,
        },
        {},
        {},
    )


@pytest.fixture
def soulmaster_stat():
    return Stat.parse_obj({
    "STR": 4915.0,
    "LUK": 1014.0,
    "INT": 1089.0,
    "DEX": 2622.0,
    "STR_multiplier": 709.0,
    "LUK_multiplier": 90.0,
    "INT_multiplier": 90.0,
    "DEX_multiplier": 90.0,
    "STR_static": 16600.0,
    "LUK_static": 280.0,
    "INT_static": 400.0,
    "DEX_static": 470.0,
    "attack_power": 2287.8,
    "magic_attack": 1238.0,
    "attack_power_multiplier": 90.0,
    "critical_rate": 81.0,
    "critical_damage": 76.0,
    "boss_damage_multiplier": 287.0,
    "damage_multiplier": 109.7,
    "ignored_defence": 95.01780376019079,
    "MHP": 25980.0,
    "MMP": 12835.0
    })
