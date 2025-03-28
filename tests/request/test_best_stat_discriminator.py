from simaple.core import ExtendedStat
from simaple.core.damage import INTBasedDamageLogic
from simaple.request.service.util import BestStatSelector, get_best_stat_index


def test_best_stat_selection() -> None:
    selector: BestStatSelector = {
        "reference_stat": ExtendedStat.model_validate(
            {
                "stat": {
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
                    "magic_attack": 2045.0,
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
                "action_stat": {"buff_duration": 50},
            }
        ),
        "damage_logic": INTBasedDamageLogic(attack_range_constant=1.0, mastery=0.95),
    }

    candidates = [
        ExtendedStat.model_validate(
            {
                "stat": {
                    "boss_damage_multiplier": 8,
                    "critical_rate": 20,
                }
            }
        ),
        ExtendedStat.model_validate(
            {
                "stat": {
                    "LUK_static": 9,
                    "INT_static": 36,
                }
            }
        ),
        ExtendedStat.model_validate(
            {
                "stat": {
                    "LUK_static": 9,
                    "INT_static": 36,
                    "INT_multiplier": 1,
                }
            }
        ),
    ]

    assert get_best_stat_index(candidates, selector) == 0
