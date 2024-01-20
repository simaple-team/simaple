import pytest

from simaple.data.skill.patch import HexaSkillImprovementPatch


@pytest.mark.parametrize(
    "level, expected",
    [
        (1, 11),
        (10, 25),
        (22, 42),
        (30, 60),
    ],
)
def test_hexa_patch(level: int, expected: int):
    target = {
        "name": "flame swip",
        "modifier": {
            "attack_power": 30.0,
        },
    }

    patch = HexaSkillImprovementPatch(improvements={"flame swip": level})

    output = patch.apply(target)

    assert output == {
        "name": "flame swip",
        "modifier": {
            "attack_power": 30.0,
            "final_damage_multiplier": expected,
        },
    }


def test_hexa_patch_with_existing_multiplier():
    target = {
        "name": "flame swip",
        "modifier": {
            "final_damage_multiplier": 100,
        },
    }

    patch = HexaSkillImprovementPatch(improvements={"flame swip": 10})

    output = patch.apply(target)

    assert output == {
        "name": "flame swip",
        "modifier": {"final_damage_multiplier": 150},
    }
