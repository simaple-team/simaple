import pytest

from simaple.simulate.component.entity import LastingStack
from simaple.simulate.component.specific.soulmaster import CosmicBurst, CosmicBurstState
from simaple.simulate.global_property import Dynamics
from tests.simulate.component.util import count_damage_skill


@pytest.fixture(name="cosmic_burst")
def fixture_cosmic_burst():
    return CosmicBurst(
        id="test",
        name="test-cosmic_burst",
        cooldown_duration=15_000,
        damage=300,
        hit=4,
        delay=690,
        damage_decrement_after_2nd_hit=0.7,
        cooltime_reduce_per_orb=1000,
    )


@pytest.fixture(name="cosmic_burst_state")
def fixture_cosmic_burst_state(
    cosmic_burst: CosmicBurst,
    dynamics: Dynamics,
):
    return CosmicBurstState.model_validate(
        {
            **cosmic_burst.get_default_state(),
            "dynamics": dynamics,
            "orb": LastingStack(maximum_stack=5, duration=30_000),
        }
    )


@pytest.mark.parametrize(
    "orb_count, cooldown_expected",
    [
        (1, 13_250),
        (5, 9_250),
    ],
)
def test_cosmic_burst_cooldown(
    cosmic_burst: CosmicBurst,
    cosmic_burst_state: CosmicBurstState,
    orb_count: int,
    cooldown_expected: float,
):
    cosmic_burst_state.orb.stack = orb_count
    cosmic_burst_state, _ = cosmic_burst.trigger(None, cosmic_burst_state)

    assert cosmic_burst_state.cooldown.time_left == cooldown_expected


def test_cosmic_burst_prevent_multiple_trigger(cosmic_burst: CosmicBurst, cosmic_burst_state: CosmicBurstState):
    cosmic_burst_state.orb.stack = 5
    cosmic_burst_state, _ = cosmic_burst.trigger(None, cosmic_burst_state)
    cosmic_burst_state, events = cosmic_burst.trigger(None, cosmic_burst_state)

    assert count_damage_skill(events) == 0
