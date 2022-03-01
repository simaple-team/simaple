import pytest
from simaple.core.base import Stat


TEST_CASES = [

    ("STR", 3, 4, 7),
    ("LUK", 3, 4, 7),
    ("INT", 3, 4, 7),
    ("DEX", 3, 4, 7),

    ("STR_multiplier", 3, 4, 7),
    ("LUK_multiplier", 3, 4, 7),
    ("INT_multiplier", 3, 4, 7),
    ("DEX_multiplier", 3, 4, 7),

    ("STR_static", 3, 4, 7),
    ("LUK_static", 3, 4, 7),
    ("INT_static", 3, 4, 7),
    ("DEX_static", 3, 4, 7),

    ("attack_power", 3, 4, 7),
    ("magic_attack", 3, 4, 7),

    ("attack_power_multiplier", 3, 4, 7),
    ("magic_attack_multiplier", 3, 4, 7),

    ("critical_rate", 3, 4, 7),
    ("critical_damage", 3, 4, 7),
    ("boss_damage_multiplier", 3, 4, 7),
    ("damage_multiplier", 3, 4, 7),
    ("final_damage_multiplier", 10, 20, 32),

    ("ignored_defence", 10, 10, 19),
]

@pytest.mark.parametrize("stat_name, a, b, c", TEST_CASES)
def test_ability(stat_name, a, b, c):
    stat_a = Stat(**{stat_name: a})
    stat_b = Stat(**{stat_name: b})

    stat_c = Stat(**{stat_name: c})

    result = stat_a + stat_b
    
    assert getattr(result, stat_name) == getattr(stat_c, stat_name)
