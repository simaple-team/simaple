import pytest

from simaple.simulate.component.specific.adele import (
    AdeleGatheringComponent,
    OrderSword,
)
from tests.simulate.component.util import count_damage_skill


@pytest.fixture(name="gathering")
def fixture_gathering(
    adele_store,
):
    component = AdeleGatheringComponent(
        name="test-gathering",
        delay=420,
        damage=650,
        hit_per_sword=4,
        cooldown=12_000,
    )
    return component.compile(adele_store)


def test_gathering_order_1pair(adele_store, gathering):
    adele_store.set_state(
        ".오더.order_sword",
        OrderSword(interval=1020, running_swords=[(0, 40000)]),
    )

    events = gathering.use(None)

    assert count_damage_skill(events) == 2


def test_gathering_order_3pair(adele_store, gathering):
    adele_store.set_state(
        ".오더.order_sword",
        OrderSword(interval=1020, running_swords=[(0, 40000), (0, 40000), (0, 40000)]),
    )

    events = gathering.use(None)

    assert count_damage_skill(events) == 6
