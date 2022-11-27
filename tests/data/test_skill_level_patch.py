import pytest

from simaple.data.passive.patch import SkillLevelPatch


def get_skill_info(passive_skill_enabled: bool, combat_orders_enabled: bool):
    return {
        "passive_skill_enabled": passive_skill_enabled,
        "combat_orders_enabled": combat_orders_enabled,
        "default_skill_level": 10,
        "stat": {
            "attack_power": "skill_level",
        },
    }


@pytest.mark.parametrize(
    "passive_skill_enabled, combat_orders_enabled, expected",
    [
        (False, False, 10),
        (False, True, 12),
        (True, False, 11),
        (True, True, 13),
    ],
)
def test_passive_skill_description_interpret(
    passive_skill_enabled, combat_orders_enabled, expected
):
    combat_orders_level = 2
    passive_skill_level = 1

    patch = SkillLevelPatch(
        combat_orders_level=combat_orders_level,
        passive_skill_level=passive_skill_level,
    )

    parsed_value = patch.apply(
        get_skill_info(passive_skill_enabled, combat_orders_enabled)
    )["stat"]["attack_power"]
    assert parsed_value == str(expected)
