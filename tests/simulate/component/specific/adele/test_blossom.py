import pytest

from simaple.core import Stat
from simaple.simulate.component.specific.adele import AdeleBlossomComponent, OrderSword
from tests.simulate.component.util import count_damage_skill


@pytest.fixture(name="blossom")
def fixture_blossom(
    adele_store,
):
    component = AdeleBlossomComponent(
        name="test-blossom",
        delay=420,
        damage=650,
        hit_per_sword=8,
        cooldown_duration=20_000,
        exceeded_stat=Stat(final_damage_multiplier=-25),
    )
    return component.compile(adele_store)


def test_blossom_order_1pair(adele_store, blossom):
    adele_store.set_state(
        ".오더.order_sword",
        OrderSword(interval=1020, running_swords=[(0, 40000)]),
    )

    events = blossom.use(None)

    assert count_damage_skill(events) == 2


def test_blossom_order_3pair(adele_store, blossom):
    adele_store.set_state(
        ".오더.order_sword",
        OrderSword(interval=1020, running_swords=[(0, 40000), (0, 40000), (0, 40000)]),
    )

    events = blossom.use(None)

    assert count_damage_skill(events) == 6
