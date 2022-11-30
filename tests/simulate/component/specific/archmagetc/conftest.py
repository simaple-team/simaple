# pylint: disable=W0621
import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
import simaple.simulate.component.specific  # pylint: disable=W0611
from simaple.core.base import ActionStat
from simaple.simulate.base import AddressedStore, ConcreteStore
from simaple.simulate.component.specific.archmagetc import FrostEffect
from simaple.simulate.global_property import GlobalProperty
from simaple.spec.repository import DirectorySpecRepository


@pytest.fixture(scope="package")
def component_repository():
    return DirectorySpecRepository("simaple/data/skill/resources/components")


@pytest.fixture
def global_property():
    return GlobalProperty(
        ActionStat(
            buff_duration=185,
            cooltime_reduce=2_000,
            summon_duration=40,
            cooltime_reduce_rate=5.0,
        )
    )


@pytest.fixture
def archmagetc_store(global_property):
    store = AddressedStore(ConcreteStore())
    global_property.install_global_properties(store)
    return store


@pytest.fixture
def frost_effect(archmagetc_store):
    frost_effect = FrostEffect(
        name="프로스트 이펙트",
        critical_damage_per_stack=3,
        maximum_stack=5,
    )

    compiled_component = frost_effect.compile(archmagetc_store)
    _ = compiled_component.frost_stack
    return compiled_component
