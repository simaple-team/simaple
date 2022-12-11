# pylint: disable=W0621
import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
import simaple.simulate.component.specific  # pylint: disable=W0611
from simaple.core.base import ActionStat
from simaple.simulate.base import AddressedStore, ConcreteStore
from simaple.simulate.global_property import GlobalProperty
from simaple.spec.repository import DirectorySpecRepository


@pytest.fixture(scope="package")
def component_repository():
    return DirectorySpecRepository("simaple/data/skill/resources/components")


@pytest.fixture
def global_property():
    return GlobalProperty(ActionStat())


@pytest.fixture
def bare_store(global_property):
    store = AddressedStore(ConcreteStore())
    global_property.install_global_properties(store)
    return store
