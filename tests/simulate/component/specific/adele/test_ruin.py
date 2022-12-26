import pytest

from simaple.simulate.component.specific.adele import AdeleRuinComponent
from simaple.simulate.reserved_names import Tag


@pytest.fixture(name="ruin")
def fixture_ruin(
    adele_store,
):
    component = AdeleRuinComponent(
        name="test-ruin",
        delay=600,
        cooldown_duration=60_000,
        red=True,
        periodic_damage_first=550,
        periodic_hit_first=6,
        periodic_interval_first=160,
        lasting_duration_first=2000,
        periodic_damage_second=990,
        periodic_hit_second=9,
        periodic_interval_second=250,
        lasting_duration_second=2000,
    )
    return component.compile(adele_store)


def test_ruin_first(ruin):
    ruin.use(None)
    events = ruin.elapse(2000)
    dealing_event = [e for e in events if e.tag == Tag.DAMAGE]

    assert len(dealing_event) == 12
    for event in dealing_event:
        assert event.payload["damage"] == 550
        assert event.payload["hit"] == 6


def test_ruin_second(ruin):
    ruin.use(None)
    ruin.elapse(2000)
    events = ruin.elapse(2000)
    dealing_event = [e for e in events if e.tag == Tag.DAMAGE]

    assert len(dealing_event) == 8
    for event in dealing_event:
        assert event.payload["damage"] == 990
        assert event.payload["hit"] == 9
