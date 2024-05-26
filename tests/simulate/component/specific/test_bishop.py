import pytest

from simaple.simulate.component.specific.bishop import HolyAdvent, HolyAdventState
from simaple.simulate.global_property import Dynamics


@pytest.fixture
def holy_advent_component():
    component = HolyAdvent(
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
        lasting_duration=1_000,
        cooldown_duration=30_000,
        synergy={},
    )
    return component


@pytest.fixture
def holy_advent_state(
    holy_advent_component: HolyAdvent,
    dynamics: Dynamics,
):
    return HolyAdventState.model_validate(
        {
            **holy_advent_component.get_default_state(),
            "dynamics": dynamics,
        }
    )


def test_holy_advent_component_emit_initial_damage(
    holy_advent_component: HolyAdvent,
    holy_advent_state: HolyAdventState,
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
