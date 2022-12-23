import pytest

from simaple.simulate.component.specific.adele import (
    AdeleGatheringComponent,
    OrderState,
)
from simaple.simulate.reserved_names import Tag


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
        ".오더.order_state",
        OrderState(interval=1020, running_swords=[(0, 40000)]),
    )

    events = gathering.use(None)
    dealing_event = [e for e in events if e.tag == Tag.DAMAGE]

    assert len(dealing_event) == 2


def test_gathering_order_3pair(adele_store, gathering):
    adele_store.set_state(
        ".오더.order_state",
        OrderState(interval=1020, running_swords=[(0, 40000), (0, 40000), (0, 40000)]),
    )

    events = gathering.use(None)
    dealing_event = [e for e in events if e.tag == Tag.DAMAGE]

    assert len(dealing_event) == 6
