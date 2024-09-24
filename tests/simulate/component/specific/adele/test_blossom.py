# pylint: disable=W0621
import pytest

from simaple.core import Stat
from simaple.simulate.component.entity import Cooldown
from simaple.simulate.component.specific.adele import (
    AdeleBlossomComponent,
    AdeleOrderUsingState,
    OrderSword,
)
from simaple.simulate.global_property import Dynamics
from tests.simulate.component.util import count_damage_skill


@pytest.fixture(name="blossom")
def fixture_blossom():
    return AdeleBlossomComponent(
        id="test",
        name="test-blossom",
        delay=420,
        damage=650,
        hit_per_sword=8,
        cooldown_duration=20_000,
        exceeded_stat=Stat(final_damage_multiplier=-25),
    )


def test_blossom_order_1pair(blossom: AdeleBlossomComponent, dynamics: Dynamics):
    # when
    _, events = blossom.use(
        None,
        AdeleOrderUsingState(
            cooldown=Cooldown(time_left=0),
            dynamics=dynamics,
            order_sword=OrderSword(interval=1020, running_swords=[(0, 40000)]),
        ),
    )

    # then
    assert count_damage_skill(events) == 2


def test_blossom_order_3pair(blossom: AdeleBlossomComponent, dynamics: Dynamics):
    # when
    _, events = blossom.use(
        None,
        AdeleOrderUsingState(
            cooldown=Cooldown(time_left=0),
            dynamics=dynamics,
            order_sword=OrderSword(interval=1020, running_swords=[(0, 40000), (0, 40000), (0, 40000)]),
        ),
    )

    # then
    assert count_damage_skill(events) == 6
