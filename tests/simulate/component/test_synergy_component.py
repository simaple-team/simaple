# pylint: disable=W0621
import pytest

from simaple.core.base import Stat
from simaple.simulate.component.complex_skill import SynergySkillComponent
from simaple.simulate.reserved_names import Tag


@pytest.fixture
def synergy():
    return Stat(attack_power=10)


@pytest.fixture
def synergy_component(synergy):
    return SynergySkillComponent(
        name="test-synergy",
        damage=100,
        hit=3,
        cooldown=60_000,
        delay=300,
        synergy=synergy,
        duration=20_000,
    )


@pytest.fixture
def compiled_synergy_component(synergy_component, bare_store):
    return synergy_component.compile(bare_store)


def test_using_frozen_synerge_component_provide_buff_and_damage(
    compiled_synergy_component, synergy
):
    events = compiled_synergy_component.use(None)

    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])

    assert dealing_count == 1
    assert compiled_synergy_component.buff() == synergy


def test_using_synerge_component_buff_do_not(compiled_synergy_component):
    compiled_synergy_component.use(None)
    events = compiled_synergy_component.elapse(30_000)

    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])
    assert dealing_count == 0
    assert compiled_synergy_component.buff() == Stat()
