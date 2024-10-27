# pylint: disable=W0621
import pytest

from simaple.core.base import Stat
from simaple.simulate.component.specific.magician import Infinity, InfinityState
from simaple.simulate.global_property import Dynamics


@pytest.fixture(name="infinity_component")
def fixture_infinity_component():
    return Infinity(
        id="test",
        name="인피니티",
        cooldown_duration=180_000,
        delay=600,
        lasting_duration=110_000,
        final_damage_increment=3,
        increase_interval=3_000,
        default_final_damage=70,
        maximum_final_damage=115,
    )


@pytest.fixture(name="infinity_state")
def fixture_infinity_state(infinity_component: Infinity, dynamics: Dynamics):
    return {**infinity_component.get_default_state(), "dynamics": dynamics}


def test_infinity_increment(
    infinity_component: Infinity, infinity_state: InfinityState
):
    # when
    state, _ = infinity_component.use(None, infinity_state)

    # then
    assert infinity_component.buff(state) == Stat(final_damage_multiplier=70)


def test_infinity_increment_during_increase(
    infinity_component: Infinity, infinity_state: InfinityState
):
    # when
    state, _ = infinity_component.use(None, infinity_state)
    state, _ = infinity_component.elapse(18_000, state)

    # then
    assert infinity_component.buff(state) == Stat(final_damage_multiplier=70 + 6 * 3)


def test_maximum_infinity_increment(
    infinity_component: Infinity, infinity_state: InfinityState
):
    state, _ = infinity_component.use(None, infinity_state)
    state, _ = infinity_component.elapse(100_000, state)

    assert infinity_component.buff(state) == Stat(final_damage_multiplier=115)


def test_infinity_stop(infinity_component: Infinity, infinity_state: InfinityState):
    state, _ = infinity_component.use(None, infinity_state)
    state, _ = infinity_component.elapse(140_000, state)

    assert infinity_component.buff(state) is None
