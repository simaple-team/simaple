# pylint: disable=W0621
import pytest

from simaple.simulate.component.specific.adele import (
    AdeleEtherComponent,
    EtherGauge,
    EtherState,
    RestoreLasting,
)
from simaple.simulate.global_property import Dynamics


@pytest.fixture(name="ether")
def fixture_ether():
    return AdeleEtherComponent(
        id="dummy",
        name="에테르",
        maximum_stack=400,
        periodic_interval=10020,
        stack_per_period=5,
        stack_per_trigger=12,
        stack_per_resonance=20,
        creation_step=100,
        order_consume=100,
    )


@pytest.fixture(name="ether_state")
def ether_state(
    ether: AdeleEtherComponent,
    dynamics: Dynamics,
):
    return {
        **ether.get_default_state(),
        "restore_lasting": RestoreLasting(time_left=0, ether_multiplier=80),
        "dynamics": dynamics,
    }


def test_ether_elapse(ether: AdeleEtherComponent, ether_state: EtherState):
    # when
    state, _ = ether.elapse(10020, ether_state)

    # then
    assert ether.running(state).stack == 5


def test_ether_divide(ether: AdeleEtherComponent, ether_state: EtherState):
    # when
    state, _ = ether.trigger(None, ether_state)

    # then
    assert ether.running(state).stack == 12


def test_ether_resonance(ether: AdeleEtherComponent, ether_state: EtherState):
    # when
    state, _ = ether.resonance(None, ether_state)

    # then
    assert ether.running(state).stack == 20


def test_ether_order_consume(ether: AdeleEtherComponent, ether_state: EtherState):
    # given
    ether_state["ether_gauge"] = EtherGauge(
        stack=100,
        maximum_stack=400,
        creation_step=100,
        order_consume=100,
    )

    # when
    ether_state, _ = ether.order(None, ether_state)

    # then
    assert ether.running(ether_state).stack == 0


def test_ether_restore_buff(ether: AdeleEtherComponent, ether_state: EtherState):
    # given
    ether_state["restore_lasting"].set_time_left(1000)

    # when
    ether_state, _ = ether.trigger(None, ether_state)

    # then
    assert ether.running(ether_state).stack == 21
