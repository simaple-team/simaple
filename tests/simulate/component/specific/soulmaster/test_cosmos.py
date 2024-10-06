import pytest

from simaple.simulate.component.entity import LastingStack
from simaple.simulate.component.specific.soulmaster import Cosmos, CosmosState
from simaple.simulate.global_property import Dynamics
from tests.simulate.component.util import count_damage_skill


@pytest.fixture(name="cosmos")
def fixture_cosmos():
    return Cosmos(
        id="test",
        name="test-cosmos",
        delay=690,
        cooldown_duration=150_000,
        periodic_interval=630,
        periodic_damage=300,
        periodic_hit=4,
        periodic_interval_decrement_per_orb=30,
        lasting_duration=15_000,
    )


@pytest.fixture(name="cosmos_state")
def fixture_cosmos_state(
    cosmos: Cosmos,
    dynamics: Dynamics,
):
    return CosmosState.model_validate(
        {
            **cosmos.get_default_state(),
            "dynamics": dynamics,
            "orb": LastingStack(maximum_stack=5, duration=30_000),
        }
    )


@pytest.mark.parametrize(
    "orb_count, count_expected",
    [
        (1, 24),
        (5, 31),
        (10, 45),
    ],
)
def test_cosmos_cooldown(
    cosmos: Cosmos,
    cosmos_state: CosmosState,
    orb_count: int,
    count_expected: int,
):
    cosmos_state.orb.stack = orb_count
    cosmos_state, _ = cosmos.use(None, cosmos_state)
    cosmos_state, events = cosmos.elapse(18_000, cosmos_state)

    assert count_damage_skill(events) == count_expected
