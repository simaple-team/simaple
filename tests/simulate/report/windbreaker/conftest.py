import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
import simaple.simulate.component.specific  # pylint: disable=W0611
from simaple.core.base import ActionStat, Stat
from simaple.simulate.kms import get_client


@pytest.fixture
def windbreaker_get_client():
    return lambda character_stat: get_client(
        ActionStat(),
        ["windbreaker", "common", "cygnus", "dex_based", "archer"],
        {
            "character_level": 276,
            "character_stat": character_stat,
            "weapon_attack_power": 789,
        },
        {
            "하울링 게일": 30,
            "아이들 윔": 30,
            "윈드 월": 30,
            "볼텍스 스피어": 30,
            "시그너스 팔랑크스": 30,
            "가이디드 애로우": 30,
            "크리티컬 리인포스": 30,
        },
        {
            "트라이플링 윔": 60,
            "핀포인트 피어스": 60,
            "천공의 노래": 60,
            "스톰 윔": 60,
            "스톰 브링어": 60,
        },
    )


@pytest.fixture
def windbreaker_stat():
    return Stat.parse_obj(
        {
            "STR": 2622.0,
            "LUK": 1014.0,
            "INT": 1089.0,
            "DEX": 4915.0,
            "STR_multiplier": 90.0,
            "LUK_multiplier": 90.0,
            "INT_multiplier": 90.0,
            "DEX_multiplier": 709.0,
            "STR_static": 470.0,
            "LUK_static": 280.0,
            "INT_static": 400.0,
            "DEX_static": 16600.0,
            "attack_power": 2287.8,
            "magic_attack": 1238.0,
            "attack_power_multiplier": 90.0,
            "critical_rate": 81.0,
            "critical_damage": 76.0,
            "boss_damage_multiplier": 287.0,
            "damage_multiplier": 109.7,
            "ignored_defence": 95.01780376019079,
            "MHP": 25980.0,
            "MMP": 12835.0,
        }
    )
