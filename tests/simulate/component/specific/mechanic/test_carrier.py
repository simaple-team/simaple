import pytest

from simaple.simulate.component.specific.mechanic import MecaCarrier
from simaple.simulate.reserved_names import Tag


@pytest.fixture(name="meca_carrier")
def fixture_multiple_option(
    mechanic_store,
):
    component = MecaCarrier(
        name="test-multiple-option",
        cooldown=180_000,
        delay=690,
        duration=120_000,
        tick_interval=3000,
        maximum_intercepter=16,
        start_intercepter=8,
        damage_per_intercepter=100,
        intercepter_penalty=120,
        hit_per_intercepter=4,
    )
    return component.compile(mechanic_store)


def test_meca_carrier_usage_increase_count(meca_carrier):
    meca_carrier.use(None)
    events = meca_carrier.elapse(30_000)

    dealing_event = [e for e in events if e.tag == Tag.DAMAGE]

    for idx in range(len(dealing_event) - 1):
        assert (
            dealing_event[idx].payload["hit"]
            == dealing_event[idx + 1].payload["hit"] - 4
        )


def test_meca_carrier_usage_delays_more(meca_carrier):
    meca_carrier.use(None)
    events = meca_carrier.elapse(3000 * 3 + 120 * (8 + 9))

    dealing_event = [e for e in events if e.tag == Tag.DAMAGE]

    assert len(dealing_event) == 3


def test_meca_carrier_usage_bounds_count(meca_carrier):
    meca_carrier.use(None)
    events = meca_carrier.elapse(120_000)

    dealing_event = [e for e in events if e.tag == Tag.DAMAGE]

    for idx in range(len(dealing_event) - 1):
        if dealing_event[idx].payload["hit"] != 64:
            assert (
                dealing_event[idx].payload["hit"]
                == dealing_event[idx + 1].payload["hit"] - 4
            )
        else:
            assert (
                dealing_event[idx].payload["hit"]
                == dealing_event[idx + 1].payload["hit"]
            )
