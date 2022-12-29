# pylint: disable=W0621
import pytest

from simaple.core.base import Stat
from simaple.simulate.component.complex_skill import SynergySkillComponent, SynergyState
from simaple.simulate.global_property import Dynamics
from simaple.simulate.reserved_names import Tag


@pytest.fixture
def synergy():
    return Stat(attack_power=10)


@pytest.fixture
def synergy_component(synergy: Stat):
    return SynergySkillComponent(
        name="test-synergy",
        damage=100,
        hit=3,
        cooldown_duration=60_000,
        delay=300,
        synergy=synergy,
        lasting_duration=20_000,
    )


@pytest.fixture
def synergy_state(synergy_component: SynergySkillComponent, dynamics: Dynamics):
    return SynergyState.parse_obj(
        {**synergy_component.get_default_state(), "dynamics": dynamics}
    )


def test_using_frozen_synerge_component_provide_buff_and_damage(
    synergy_component: SynergySkillComponent,
    synergy_state: SynergyState,
    synergy: Stat,
):
    # when
    state, events = synergy_component.use(None, synergy_state)

    # then
    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])

    assert dealing_count == 1
    assert synergy_component.buff(state) == synergy


def test_using_synerge_component_buff_do_not(
    synergy_component: SynergySkillComponent,
    synergy_state: SynergyState,
):
    # when
    state, _ = synergy_component.use(None, synergy_state)
    state, events = synergy_component.elapse(30_000, state)

    # then
    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])
    assert dealing_count == 0
    assert synergy_component.buff(state) == Stat()
