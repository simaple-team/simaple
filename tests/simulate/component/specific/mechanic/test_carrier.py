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
        cooldown_duration=200_000,
        delay=690,
        lasting_duration=120_000,
        periodic_interval=3000,
        maximum_intercepter=16,
        start_intercepter=8,
        damage_per_intercepter=100,
        intercepter_penalty=120,
        hit_per_intercepter=4,
    )


@pytest.fixture(name="meca_carrier_state")
def meca_carrier_state(
    meca_carrier: MecaCarrier, dynamics: Dynamics, robot_mastery: RobotMastery
):
    return MecaCarrierState.parse_obj(
        {
            **meca_carrier.get_default_state(),
            "dynamics": dynamics,
            "robot_mastery": robot_mastery,
        }
    )


def test_meca_carrier_usage_increase_count(
    meca_carrier: MecaCarrier, meca_carrier_state: MecaCarrierState
):
    # when
    state, _ = meca_carrier.use(None, meca_carrier_state)
    state, events = meca_carrier.elapse(30_000, state)

    # then
    dealing_event = [e for e in events if e.tag == Tag.DAMAGE]

    for idx in range(len(dealing_event) - 1):
        assert (
            dealing_event[idx].payload["hit"]
            == dealing_event[idx + 1].payload["hit"] - 4
        )


def test_meca_carrier_usage_delays_more(
    meca_carrier: MecaCarrier, meca_carrier_state: MecaCarrierState
):
    # when
    state, _ = meca_carrier.use(None, meca_carrier_state)
    state, events = meca_carrier.elapse(3000 * 3 + 120 * (8 + 9), state)

    # then
    dealing_event = [e for e in events if e.tag == Tag.DAMAGE]

    assert len(dealing_event) == 3


def test_meca_carrier_usage_bounds_count(
    meca_carrier: MecaCarrier, meca_carrier_state: MecaCarrierState
):
    # when
    state, _ = meca_carrier.use(None, meca_carrier_state)
    state, events = meca_carrier.elapse(120_000, state)

    # then
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
