# pylint: disable=W0621
import pytest

from simaple.simulate.component.common.multiple_hit_hexa_skill import (
    MultipleHitHexaSkillComponent,
    MultipleHitHexaSkillState,
)
from simaple.simulate.global_property import Dynamics


@pytest.fixture
def multiple_hit_skill():
    component = MultipleHitHexaSkillComponent(
        id="test",
        name="periodic-damage-component",
        damage_and_hits=[{"damage": 100, "hit": 1}, {"damage": 200, "hit": 3}],
        delay=30,
        cooldown_duration=30_000,
    )
    return component


@pytest.fixture
def multiple_hit_skill_state(
    multiple_hit_skill: MultipleHitHexaSkillComponent,
    dynamics: Dynamics,
):
    return {
        **multiple_hit_skill.get_default_state(),
        "dynamics": dynamics,
    }


def test_multiple_hit_skill(
    multiple_hit_skill: MultipleHitHexaSkillComponent,
    multiple_hit_skill_state: MultipleHitHexaSkillState,
):
    # given
    _, events = multiple_hit_skill.use(None, multiple_hit_skill_state)

    # then
    assert events[0]["payload"] == {"damage": 100, "hit": 1.0, "modifier": None}
    assert events[1]["payload"] == {"damage": 200, "hit": 3.0, "modifier": None}
    assert events[2]["payload"] == {"time": 30.0}
