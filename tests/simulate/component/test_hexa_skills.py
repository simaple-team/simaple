# pylint: disable=W0621
import pytest

from simaple.simulate.component.common.multiple_hit_hexa_skill import (
    MultipleHitHexaSkillComponent,
    MultipleHitHexaSkillState,
)
from simaple.simulate.component.common.triple_periodic_damage_hexa_skill import (
    TriplePeriodicDamageHexaComponent,
    TriplePeriodicDamageHexaComponentState,
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


@pytest.fixture
def holy_advent_component():
    component = TriplePeriodicDamageHexaComponent(
        id="test",
        name="periodic-damage-component",
        damage_and_hits=[{"damage": 100, "hit": 1}, {"damage": 200, "hit": 3}],
        delay=30,
        periodic_01={
            "interval": 120,
            "damage": 50,
            "hit": 3,
        },
        periodic_02={
            "interval": 120,
            "damage": 50,
            "hit": 3,
        },
        periodic_03={
            "interval": 60,
            "damage": 50,
            "hit": 3,
        },
        lasting_duration=1000_000,
        cooldown_duration=30_000,
        synergy={},
    )
    return component


@pytest.fixture
def holy_advent_state(
    holy_advent_component: TriplePeriodicDamageHexaComponent,
    dynamics: Dynamics,
):
    return {
        **holy_advent_component.get_default_state(),
        "dynamics": dynamics,
    }


def test_holy_advent_component_emit_initial_damage(
    holy_advent_component: TriplePeriodicDamageHexaComponent,
    holy_advent_state: TriplePeriodicDamageHexaComponentState,
):
    # given
    holy_advent_state, events = holy_advent_component.use(None, holy_advent_state)

    # then
    assert len(events) == 3

    assert events[0]["payload"] == {"damage": 100, "hit": 1.0, "modifier": None}
    assert events[1]["payload"] == {"damage": 200, "hit": 3.0, "modifier": None}
    assert events[2]["payload"] == {"time": 30.0}

    holy_advent_state, events = holy_advent_component.elapse(120.1, holy_advent_state)

    assert len(events) == 5  # 1+1+2 event + 1(elapse)

    holy_advent_state, events = holy_advent_component.elapse(240, holy_advent_state)

    assert len(events) == 9  # 2+2+4 event + 1(elapse)
