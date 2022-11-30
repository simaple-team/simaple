import pytest

from simaple.core.base import Stat
from simaple.simulate.component.specific.archmagetc import ThunderBreak
from simaple.simulate.reserved_names import Tag


@pytest.fixture(name="thunder_break")
def fixture_thunder_break(frost_effect, archmagetc_store):
    component = ThunderBreak(
        name="test-thunder-break",
        delay=690,
        cooldown=40_000,
        tick_interval=120,
        tick_damage=925,
        tick_hit=12,
        duration=10_000,
        decay_rate=0.8,
        max_count=8,
    )
    return component.compile(archmagetc_store)


def test_thunder_break_max_use(thunder_break):
    thunder_break.use(None)
    events = thunder_break.elapse(12_000)

    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])

    assert dealing_count == 8


def test_thunder_break_decays(thunder_break):
    thunder_break.use(None)
    dealing_events = [e for e in thunder_break.elapse(12_000) if e.tag == Tag.DAMAGE]

    for idx in range(7):
        assert (
            dealing_events[idx].payload["damage"] * 0.8
            - dealing_events[idx + 1].payload["damage"]
        ) < 1e-8
