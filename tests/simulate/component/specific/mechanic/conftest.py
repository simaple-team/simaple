# pylint: disable=W0621
import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
import simaple.simulate.component.specific  # pylint: disable=W0611
from simaple.core.base import ActionStat
from simaple.simulate.base import AddressedStore, ConcreteStore
from simaple.simulate.component.specific.mechanic import RobotMastery
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
def mechanic_store(global_property):
    store = AddressedStore(ConcreteStore())
    global_property.install_global_properties(store)
    store.set_state(
        ".로봇 마스터리.robot_mastery",
        RobotMastery(
            summon_increment=40,
            robot_damage_increment=5,
            robot_buff_damage_multiplier=100,
        ),
    )
    return store
