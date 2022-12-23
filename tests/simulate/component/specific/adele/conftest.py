# pylint: disable=W0621
import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
import simaple.simulate.component.specific  # pylint: disable=W0611
from simaple.core.base import ActionStat
from simaple.simulate.base import AddressedStore, ConcreteStore
from simaple.simulate.component.skill import AttackSkillComponent
from simaple.simulate.component.specific.adele import AdeleEtherComponent, EtherState
from simaple.simulate.component.specific.archmagetc import FrostEffect
from simaple.simulate.component.state import IntervalState
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
        ".에테르.ether_state",
        EtherState(maximum_stack=400),
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
    )

    compiled_component = ether.compile(adele_store)
    _ = compiled_component.ether_state
    return compiled_component


@pytest.fixture
def divide(adele_store):
    divide = AttackSkillComponent(name="디바이드", delay=600, damage=375, hit=6)

    compiled_component = divide.compile(adele_store)
    return compiled_component
