import pytest
from simaple.core.base import Ability, Stat

ABILITY_TEST_CASE = [
    ("STR", 3, 4, 7),
    ("LUK", 3, 4, 7),
    ("INT", 3, 4, 7),
    ("DEX", 3, 4, 7),
]

@pytest.mark.parametrize("stat_name, a, b, c", ABILITY_TEST_CASE)
def test_ability(stat_name, a, b, c):
    ability_a = Ability(**{stat_name: a})
    ability_b = Ability(**{stat_name: b})

    ability_c = Ability(**{stat_name: c})

    result = ability_a + ability_b
    
    assert getattr(result, stat_name) == getattr(ability_c, stat_name)


TEST_CASES = [
    ("ability", Ability(STR=3), Ability(STR=4), Ability(STR=7)),
    ("ability_multiplier", Ability(STR=3), Ability(STR=4), Ability(STR=7)),
    ("ability_static", Ability(STR=3), Ability(STR=4), Ability(STR=7)),

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
