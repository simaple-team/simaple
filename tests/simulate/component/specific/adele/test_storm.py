import pytest

from simaple.simulate.component.specific.adele import AdeleStormComponent, OrderSword
from simaple.simulate.reserved_names import Tag


@pytest.fixture(name="storm")
def fixture_storm(
    adele_store,
):
    component = AdeleStormComponent(
        name="test-storm",
        delay=780,
        cooldown_duration=90_000,
        periodic_interval=330,
        periodic_damage=550,
        periodic_hit=1,
        lasting_duration=14000,
        maximum_stack=8,
    )
    return component.compile(adele_store)


def test_storm_order_1pair(adele_store, storm):
    adele_store.set_state(
        ".오더.order_sword",
        OrderSword(interval=1020, running_swords=[(0, 40000)]),
    )

    storm.use(None)
    events = storm.elapse(500)
    dealing_event = [e for e in events if e.tag == Tag.DAMAGE]

    assert dealing_event[0].payload["hit"] == 2


def test_storm_order_3pair(adele_store, storm):
    adele_store.set_state(
        ".오더.order_sword",
        OrderSword(interval=1020, running_swords=[(0, 40000), (0, 40000), (0, 40000)]),
    )

    storm.use(None)
    events = storm.elapse(500)
    dealing_event = [e for e in events if e.tag == Tag.DAMAGE]

    assert dealing_event[0].payload["hit"] == 6
