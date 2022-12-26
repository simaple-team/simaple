# pylint: disable=W0621
import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
import simaple.simulate.component.specific  # pylint: disable=W0611
from simaple.core.base import ActionStat
from simaple.simulate.base import AddressedStore, ConcreteStore
from simaple.simulate.component.specific.adele import (
    AdeleEtherComponent,
    AdeleOrderComponent,
    EtherGauge,
    RestoreLasting,
)
from simaple.simulate.global_property import GlobalProperty
from simaple.spec.repository import DirectorySpecRepository


@pytest.fixture(scope="package")
def component_repository():
    return DirectorySpecRepository("simaple/data/skill/resources/components")


@pytest.fixture
def global_property():
    return GlobalProperty(
        ActionStat(
            cooltime_reduce=0,
            cooltime_reduce_rate=5.0,
        )
    )


@pytest.fixture
def adele_store(global_property):
    store = AddressedStore(ConcreteStore())
    global_property.install_global_properties(store)
    store.set_state(
        ".에테르.ether_gauge",
        EtherGauge(
            maximum_stack=400,
            creation_step=100,
            order_consume=100,
        ),
    )
    store.set_state(
        ".리스토어(버프).lasting",
        RestoreLasting(time_left=0, ether_multiplier=80),
    )
    return store


@pytest.fixture
def ether(adele_store):
    ether = AdeleEtherComponent(
        name="에테르",
        maximum_stack=400,
        tick_interval=10020,
        stack_per_tick=5,
        stack_per_trigger=12,
        stack_per_resonance=20,
        creation_step=100,
        order_consume=100,
    )

    compiled_component = ether.compile(adele_store)
    _ = compiled_component.ether_gauge
    return compiled_component


@pytest.fixture(name="order")
def fixture_order(
    adele_store,
):
    component = AdeleOrderComponent(
        name="test-order",
        delay=0,
        cooldown_duration=500,
        lasting_duration=40000,
        tick_interval=1020,
        tick_damage=360,
        tick_hit=2,
        maximum_stack=6,
        restore_maximum_stack=8,
    )
    return component.compile(adele_store)
