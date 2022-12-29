# pylint: disable=W0621
import pytest

from simaple.simulate.component.specific.adele import (
    AdeleGatheringComponent,
    AdeleOrderUsingState,
    OrderSword,
)
from simaple.simulate.global_property import Dynamics
from tests.simulate.component.util import count_damage_skill


@pytest.fixture(name="gathering")
def fixture_gathering():
    return AdeleGatheringComponent(
        name="test-gathering",
        delay=420,
        damage=650,
        hit_per_sword=4,
        cooldown_duration=12_000,
    )


@pytest.fixture(name="gathering_state_1pair")
def gathering_state_1pair(
    gathering: AdeleGatheringComponent,
    dynamics: Dynamics,
):
    return AdeleOrderUsingState.parse_obj(
        {
            **gathering.get_default_state(),
            "order_sword": OrderSword(interval=1020, running_swords=[(0, 40000)]),
            "dynamics": dynamics,
        }
    )


@pytest.fixture(name="gathering_state_3pair")
def gathering_state_3pair(
    gathering: AdeleGatheringComponent,
    dynamics: Dynamics,
):
    return AdeleOrderUsingState.parse_obj(
        {
            **gathering.get_default_state(),
            "order_sword": OrderSword(
                interval=1020, running_swords=[(0, 40000), (0, 40000), (0, 40000)]
            ),
            "dynamics": dynamics,
        }
    )


def test_gathering_order_1pair(
    gathering: AdeleGatheringComponent, gathering_state_1pair: AdeleOrderUsingState
):
    _, events = gathering.use(None, gathering_state_1pair)

    assert count_damage_skill(events) == 2


def test_gathering_order_3pair(
    gathering: AdeleGatheringComponent, gathering_state_3pair: AdeleOrderUsingState
):
    _, events = gathering.use(None, gathering_state_3pair)

    assert count_damage_skill(events) == 6
