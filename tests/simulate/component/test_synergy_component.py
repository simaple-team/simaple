# pylint: disable=W0621
import pytest

from simaple.core.base import Stat
from simaple.simulate.global_property import Dynamics
from simaple.simulate.reserved_names import Tag

from simaple.simulate.component.complex_skill import SynergySkillComponent



@pytest.fixture
def synergy():
    return Stat(
        attack_power=10
    )


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


def test_using_synerge_component_provide_buff_and_damage(synergy_component, dynamics, synergy):
    default_state = synergy_component.get_default_state()

    cooldown_state = default_state.get("cooldown_state")
    duration_state = default_state.get("duration_state")

    (cooldown_state, duration_state, dynamics), events = synergy_component.use(
        None, cooldown_state, duration_state, dynamics
    )

    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])

    assert dealing_count == 1
    assert synergy_component.buff(duration_state) == synergy


def test_using_synerge_component_buff_do_not(synergy_component, dynamics, synergy):
    default_state = synergy_component.get_default_state()

    cooldown_state = default_state.get("cooldown_state")
    duration_state = default_state.get("duration_state")

    (cooldown_state, duration_state, dynamics), _ = synergy_component.use(
        None, cooldown_state, duration_state, dynamics
    )

    (cooldown_state, duration_state), events = synergy_component.elapse(
        30_000, cooldown_state, duration_state,
    )

    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])
    assert dealing_count == 0
    assert synergy_component.buff(duration_state) == Stat()
