# pylint: disable=W0621
import pytest

from simaple.simulate.component.specific.adele import (
    AdeleStormComponent,
    AdeleStormState,
    OrderSword,
)
from simaple.simulate.global_property import Dynamics
from simaple.simulate.reserved_names import Tag


@pytest.fixture(name="storm")
def fixture_storm():
    return AdeleStormComponent(
        id="test",
        name="test-storm",
        delay=780,
        cooldown_duration=90_000,
        periodic_interval=330,
        periodic_damage=550,
        periodic_hit=1,
        lasting_duration=14000,
        maximum_stack=8,
    )


@pytest.fixture(name="storm_state_1pair")
def storm_state_1pair(
    storm: AdeleStormComponent,
    dynamics: Dynamics,
):
    return AdeleStormState.model_validate(
        {
            **storm.get_default_state(),
            "order_sword": OrderSword(interval=1020, running_swords=[(0, 40000)]),
            "dynamics": dynamics,
        }
    )


@pytest.fixture(name="storm_state_3pair")
def storm_state_3pair(
    storm: AdeleStormComponent,
    dynamics: Dynamics,
):
    return AdeleStormState.model_validate(
        {
            **storm.get_default_state(),
            "order_sword": OrderSword(
                interval=1020, running_swords=[(0, 40000), (0, 40000), (0, 40000)]
            ),
            "dynamics": dynamics,
        }
    )


def test_storm_order_1pair(
    storm: AdeleStormComponent, storm_state_1pair: AdeleStormState
):
    state, _ = storm.use(None, storm_state_1pair)
    _, events = storm.elapse(500, state)
    dealing_event = [e for e in events if e["tag"] == Tag.DAMAGE]

    assert dealing_event[0]["payload"]["hit"] == 2


def test_storm_order_3pair(
    storm: AdeleStormComponent, storm_state_3pair: AdeleStormState
):
    state, _ = storm.use(None, storm_state_3pair)
    _, events = storm.elapse(500, state)
    dealing_event = [e for e in events if e["tag"] == Tag.DAMAGE]

    assert dealing_event[0]["payload"]["hit"] == 6
