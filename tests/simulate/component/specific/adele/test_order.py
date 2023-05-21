# pylint: disable=W0621
import pytest

from simaple.simulate.component.specific.adele import (
    AdeleOrderComponent,
    AdeleOrderState,
    EtherGauge,
    RestoreLasting,
)
from simaple.simulate.global_property import Dynamics


@pytest.fixture(name="order")
def fixture_order():
    return AdeleOrderComponent(
        id="test",
        name="test-order",
        delay=0,
        cooldown_duration=500,
        lasting_duration=40000,
        periodic_interval=1020,
        periodic_damage=360,
        periodic_hit=2,
        maximum_stack=6,
        restore_maximum_stack=8,
    )


@pytest.fixture(name="order_state")
def order_state(
    order: AdeleOrderComponent,
    dynamics: Dynamics,
):
    return AdeleOrderState.parse_obj(
        {
            **order.get_default_state(),
            "ether_gauge": EtherGauge(
                stack=400,
                maximum_stack=400,
                creation_step=100,
                order_consume=100,
            ),
            "restore_lasting": RestoreLasting(time_left=0, ether_multiplier=80),
            "dynamics": dynamics,
        }
    )


def test_order_count(order: AdeleOrderComponent, order_state: AdeleOrderState):
    state, _ = order.use(None, order_state)
    state, _ = order.elapse(500, state)
    state, _ = order.use(None, state)
    state, _ = order.elapse(500, state)
    state, _ = order.use(None, state)

    assert order.running(state).stack == 6


def test_order_elapse(order: AdeleOrderComponent, order_state: AdeleOrderState):
    order_state.order_sword.running_swords = [(0, 20000), (0, 30000), (0, 40000)]

    state, _ = order.elapse(20000, order_state)
    assert order.running(state).stack == 4

    state, _ = order.elapse(10000, state)
    assert order.running(state).stack == 2

    state, _ = order.elapse(10000, state)
    assert order.running(state).stack == 0
