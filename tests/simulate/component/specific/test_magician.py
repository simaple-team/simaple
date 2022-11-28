import pytest

from simaple.core.base import Stat
from simaple.simulate.component.specific.magician import Infinity


@pytest.fixture(name="infinity_component")
def fixture_infinity_component(bare_store):
    infinity = Infinity(
        name="인피니티",
        cooldown=180_000,
        delay=600,
        duration=120_000,
        final_damage_increment=3,
        increase_interval=3_000,
        default_final_damage=70,
        maximum_final_damage=115,
    )

    return infinity.compile(bare_store)


def test_infinity_increment(infinity_component):
    infinity_component.use(None)

    assert infinity_component.buff() == Stat(final_damage_multiplier=70)


def test_infinity_increment_during_increase(infinity_component):
    infinity_component.use(None)
    infinity_component.elapse(18_000)

    assert infinity_component.buff() == Stat(final_damage_multiplier=70 + 6 * 3)


def test_maximum_infinity_increment(infinity_component):
    infinity_component.use(None)
    infinity_component.elapse(100_000)

    assert infinity_component.buff() == Stat(final_damage_multiplier=115)


def test_infinity_stop(infinity_component):
    infinity_component.use(None)
    infinity_component.elapse(140_000)

    assert infinity_component.buff() is None
