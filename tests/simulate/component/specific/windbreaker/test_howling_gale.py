import pytest

from simaple.simulate.component.specific.windbreaker import (
    HowlingGaleComponent,
    HowlingGaleState,
)
from simaple.simulate.global_property import Dynamics
from tests.simulate.component.util import count_damage_skill


@pytest.fixture(name="howling_gale")
def fixture_howling_gale():
    return HowlingGaleComponent(
        id="test",
        name="test-howling-gale",
        delay=630,
        maximum_stack=3,
        cooldown_duration=20_000,
        periodic_interval=150,
        periodic_damage=[[500], [1000], [1000, 700]],
        periodic_hit=[[3], [3], [3, 3]],
        lasting_duration=9_850,
    )


@pytest.fixture(name="howling_gale_state")
def fixture_blade_storm_state(howling_gale: HowlingGaleComponent, dynamics: Dynamics):
    return HowlingGaleState.model_validate({**howling_gale.get_default_state(), "dynamics": dynamics})


def test_default_stack(howling_gale: HowlingGaleComponent, howling_gale_state: HowlingGaleState):
    assert howling_gale_state.consumable.get_stack() == 3


def test_refill_stack(howling_gale: HowlingGaleComponent, howling_gale_state: HowlingGaleState):
    used_state, _ = howling_gale.use(None, howling_gale_state)
    assert used_state.consumable.get_stack() == 0

    state, _ = howling_gale.elapse(20_000, used_state)
    assert state.consumable.get_stack() == 1

    state, _ = howling_gale.elapse(59_000, used_state)
    assert state.consumable.get_stack() == 2

    state, _ = howling_gale.elapse(60_000, used_state)
    assert state.consumable.get_stack() == 3


def test_initial_hit_delay(howling_gale: HowlingGaleComponent, howling_gale_state: HowlingGaleState):
    howling_gale_state.consumable.stack = 1
    state, events = howling_gale.use(None, howling_gale_state)
    assert count_damage_skill(events) == 0

    state, events = howling_gale.elapse(630, state)
    assert count_damage_skill(events) == 1


@pytest.mark.parametrize(
    "stack, total_hits",
    [
        (1, 66),
        (2, 66),
        (3, 66 * 2),
    ],
)
def test_total_hits(
    howling_gale: HowlingGaleComponent,
    howling_gale_state: HowlingGaleState,
    stack: int,
    total_hits: int,
):
    howling_gale_state.consumable.stack = stack
    state, _ = howling_gale.use(None, howling_gale_state)
    state, events = howling_gale.elapse(15_000, state)

    assert count_damage_skill(events) == total_hits
