import pytest

from simaple.simulate.component.specific.dualblade import (
    BladeStormComponent,
    BladeStormState,
)
from simaple.simulate.global_property import Dynamics
from tests.simulate.component.util import count_damage_skill


@pytest.fixture(name="blade_storm")
def fixture_blade_storm():
    return BladeStormComponent(
        id="test",
        name="test-blade-storm",
        damage=960,
        delay=120,
        hit=5,
        maximum_keydown_time=5000,
        keydown_prepare_delay=120,
        prepare_damage=1270,
        prepare_hit=7,
        keydown_end_delay=120,
        cooldown_duration=90_000,
    )


@pytest.fixture(name="blade_storm_state")
def fixture_blade_storm_state(blade_storm: BladeStormComponent, dynamics: Dynamics):
    return {**blade_storm.get_default_state(), "dynamics": dynamics}


def test_prepare_damage(
    blade_storm: BladeStormComponent, blade_storm_state: BladeStormState
):
    # when
    state, events = blade_storm.use(None, blade_storm_state)

    # then
    assert count_damage_skill(events) == 1
