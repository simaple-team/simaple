import pytest

from simaple.core import Stat
from simaple.simulate.component.skill import AlwaysEnabledComponent, NoState


@pytest.fixture(name="always_enabled_component")
def fixture_always_enabled_component():
    return AlwaysEnabledComponent(
        name="always-enabled",
        stat=Stat(attack_power=30),
    )


def test_running(always_enabled_component: AlwaysEnabledComponent):
    running = always_enabled_component.running(NoState())
    assert running.time_left > 0


def test_buff(always_enabled_component: AlwaysEnabledComponent):
    stat = always_enabled_component.buff(NoState())
    assert stat == Stat(attack_power=30)
