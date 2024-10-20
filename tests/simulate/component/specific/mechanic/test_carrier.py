# pylint: disable=W0621
import pytest

from simaple.simulate.component.specific.mechanic import (
    MecaCarrier,
    MecaCarrierState,
    RobotMastery,
)
from simaple.simulate.global_property import Dynamics
from simaple.simulate.reserved_names import Tag


@pytest.fixture(name="meca_carrier")
def fixture_meca_carrier():
    return MecaCarrier(
        id="test",
        name="test-meca-carrier",
        cooldown_duration=180_000,
        delay=720,
        lasting_duration=70_000,
        periodic_interval=2850,
        maximum_intercepter=16,
        start_intercepter=9,
        damage_per_intercepter=100,
        intercepter_penalty=120,
        hit_per_intercepter=4,
    )


@pytest.fixture(name="meca_carrier_state")
def meca_carrier_state(
    meca_carrier: MecaCarrier, dynamics: Dynamics, robot_mastery: RobotMastery
):
    return {
        **meca_carrier.get_default_state(),
        "dynamics": dynamics,
        "robot_mastery": robot_mastery,
    }


def test_meca_carrier_usage_count(
    meca_carrier: MecaCarrier, meca_carrier_state: MecaCarrierState
):
    state, _ = meca_carrier.use(None, meca_carrier_state)

    state, events = meca_carrier.elapse(0, state)
    dealing_event = [e for e in events if e["tag"] == Tag.DAMAGE]
    assert len(dealing_event) == 9

    state, events = meca_carrier.elapse(2850 + 120 * 9, state)
    dealing_event = [e for e in events if e["tag"] == Tag.DAMAGE]
    assert len(dealing_event) == 10

    state, events = meca_carrier.elapse(2850 + 120 * 10, state)
    dealing_event = [e for e in events if e["tag"] == Tag.DAMAGE]
    assert len(dealing_event) == 11

    state, events = meca_carrier.elapse(2850 + 120 * 11, state)
    dealing_event = [e for e in events if e["tag"] == Tag.DAMAGE]
    assert len(dealing_event) == 12

    state, events = meca_carrier.elapse(2850 + 120 * 12, state)
    dealing_event = [e for e in events if e["tag"] == Tag.DAMAGE]
    assert len(dealing_event) == 13

    state, events = meca_carrier.elapse(2850 + 120 * 13, state)
    dealing_event = [e for e in events if e["tag"] == Tag.DAMAGE]
    assert len(dealing_event) == 14

    state, events = meca_carrier.elapse(2850 + 120 * 14, state)
    dealing_event = [e for e in events if e["tag"] == Tag.DAMAGE]
    assert len(dealing_event) == 15

    state, events = meca_carrier.elapse(2850 + 120 * 15, state)
    dealing_event = [e for e in events if e["tag"] == Tag.DAMAGE]
    assert len(dealing_event) == 16

    state, events = meca_carrier.elapse(2850 + 120 * 16, state)
    dealing_event = [e for e in events if e["tag"] == Tag.DAMAGE]
    assert len(dealing_event) == 16

    state, events = meca_carrier.elapse(2850 + 120 * 16, state)
    dealing_event = [e for e in events if e["tag"] == Tag.DAMAGE]
    assert len(dealing_event) == 16


def test_meca_carrier_total_hit_count(
    meca_carrier: MecaCarrier, meca_carrier_state: MecaCarrierState
):
    # when
    state, _ = meca_carrier.use(None, meca_carrier_state)
    state, events = meca_carrier.elapse(120_000, state)

    # then
    dealing_event = [e for e in events if e["tag"] == Tag.DAMAGE]
    hit_count = sum(e["payload"]["hit"] for e in dealing_event)

    assert hit_count == (9 + 10 + 11 + 12 + 13 + 14 + 15 + 16 * 9) * 4
