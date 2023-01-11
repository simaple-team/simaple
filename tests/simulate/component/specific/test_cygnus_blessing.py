# pylint: disable=W0621
import pytest

from simaple.core.base import Stat
from simaple.simulate.component.specific.cygnus import (
    TranscendentCygnusBlessing,
    TranscendentCygnusBlessingState,
)
from simaple.simulate.global_property import Dynamics


@pytest.fixture(name="cygnus_blessing_component")
def fixture_cygnus_blessing_component():
    return TranscendentCygnusBlessing(
        name="초월자 시그너스의 축복",
        cooldown_duration=180_000,
        delay=600,
        lasting_duration=110_000,
        damage_increment=3,
        increase_interval=3_000,
        default_damage=70,
        maximum_damage=115,
        maximum_stack=2,
    )


@pytest.fixture(name="cygnus_blessing_state")
def fixture_cygnus_blessing_state(
    cygnus_blessing_component: TranscendentCygnusBlessing, dynamics: Dynamics
):
    return TranscendentCygnusBlessingState.parse_obj(
        {**cygnus_blessing_component.get_default_state(), "dynamics": dynamics}
    )


def test_cygnus_blessing_increment(
    cygnus_blessing_component: TranscendentCygnusBlessing,
    cygnus_blessing_state: TranscendentCygnusBlessingState,
):
    # when
    state, _ = cygnus_blessing_component.use(None, cygnus_blessing_state)

    # then
    assert cygnus_blessing_component.buff(state) == Stat(damage_multiplier=70)


def test_cygnus_blessing_increment_during_increase(
    cygnus_blessing_component: TranscendentCygnusBlessing,
    cygnus_blessing_state: TranscendentCygnusBlessingState,
):
    # when
    state, _ = cygnus_blessing_component.use(None, cygnus_blessing_state)
    state, _ = cygnus_blessing_component.elapse(18_000, state)

    # then
    assert cygnus_blessing_component.buff(state) == Stat(damage_multiplier=70 + 6 * 3)


def test_maximum_cygnus_blessing_increment(
    cygnus_blessing_component: TranscendentCygnusBlessing,
    cygnus_blessing_state: TranscendentCygnusBlessingState,
):
    state, _ = cygnus_blessing_component.use(None, cygnus_blessing_state)
    state, _ = cygnus_blessing_component.elapse(100_000, state)

    assert cygnus_blessing_component.buff(state) == Stat(damage_multiplier=115)


def test_cygnus_blessing_stop(
    cygnus_blessing_component: TranscendentCygnusBlessing,
    cygnus_blessing_state: TranscendentCygnusBlessingState,
):
    state, _ = cygnus_blessing_component.use(None, cygnus_blessing_state)
    state, _ = cygnus_blessing_component.elapse(140_000, state)

    assert cygnus_blessing_component.buff(state) is None
