import math
import os

import pytest
import yaml

from simaple.core import Stat
from simaple.job.passive_skill import (
    PassiveSkillArgument,
    PassiveSkillDescription,
    PassiveSkillResource,
    PassiveSkillset,
)


@pytest.fixture(name="test_passive_skill_resource_filename")
def fixture_test_passive_skill_resource_filename():
    return os.path.join(
        os.path.dirname(__file__), "resources", "test_passive_skill.yaml"
    )


@pytest.fixture(name="test_passive_skill_resource")
def fixture_test_passive_skill_resource(test_passive_skill_resource_filename):
    with open(test_passive_skill_resource_filename, "r", encoding="utf-8") as f:
        values = yaml.safe_load(f)

    return PassiveSkillResource.parse_obj(values)


@pytest.mark.parametrize(
    "passive_skill_enabled, combat_orders_enabled, default_skill_level",
    [
        (False, False, 7),
        (False, True, 7),
        (True, False, 7),
        (True, True, 7),
        (True, True, 10),
    ],
)
def test_passive_skill_description_interpret(
    passive_skill_enabled, combat_orders_enabled, default_skill_level
):
    combat_orders_level = 2
    passive_skill_level = 1
    description = PassiveSkillDescription(
        stat={"STR": 3, "LUK": "3 + lv * 2", "INT": "3 + math.floor(lv / 4)"},
        name="test_passive_skill",
        passive_skill_enabled=passive_skill_enabled,
        combat_orders_enabled=combat_orders_enabled,
        default_skill_level=default_skill_level,
    )

    passive_skill = description.interpret(
        PassiveSkillArgument(
            combat_orders_level=combat_orders_level,
            passive_skill_level=passive_skill_level,
            character_level=260,
        )
    )

    expected_level = (
        default_skill_level
        + int(passive_skill_enabled) * passive_skill_level
        + int(combat_orders_enabled) * combat_orders_level
    )
    assert passive_skill.name == "test_passive_skill"
    assert passive_skill.stat == Stat(
        STR=3, LUK=3 + expected_level * 2, INT=3 + math.floor(expected_level / 4)
    )


@pytest.mark.parametrize(
    "skill_name",
    ["test_passive_1", "test_passive_2", "test_passive_3", "test_passive_4"],
)
def test_passive_skill_repository(test_passive_skill_resource_filename, skill_name):
    skill_set = PassiveSkillset.from_resource_file(test_passive_skill_resource_filename)
    argument = PassiveSkillArgument(
        combat_orders_level=2,
        passive_skill_level=1,
        character_level=260,
    )
    skill_set.get(skill_name, argument)
