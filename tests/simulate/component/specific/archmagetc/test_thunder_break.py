# pylint: disable=W0621
import pytest

from simaple.simulate.component.entity import Periodic
from simaple.simulate.component.specific.archmagetc import (
    FrostEffectState,
    ThunderBreak,
    ThunderBreakState,
)
from simaple.simulate.global_property import Dynamics
from simaple.simulate.reserved_names import Tag


@pytest.fixture(name="thunder_break")
def fixture_thunder_break():
    return ThunderBreak(
        id="test",
        name="test-thunder-break",
        delay=690,
        cooldown_duration=40_000,
        periodic_interval=120,
        periodic_damage=925,
        periodic_hit=12,
        lasting_duration=10_000,
        decay_rate=0.8,
        max_count=8,
    )


@pytest.fixture(name="thunder_break_state")
def thunder_break_state(
    thunder_break: ThunderBreak,
    frost_effect_state: FrostEffectState,
    jupyter_thunder_periodic: Periodic,
    dynamics: Dynamics,
):
    return ThunderBreakState.model_validate(
        {
            **thunder_break.get_default_state(),
            "frost_stack": frost_effect_state.frost_stack,
            "jupyter_thunder_shock": jupyter_thunder_periodic,
            "dynamics": dynamics,
        }
    )


def test_thunder_break_max_use(
    thunder_break: ThunderBreak, thunder_break_state: ThunderBreakState
):
    # when
    state, _ = thunder_break.use(None, thunder_break_state)
    state, events = thunder_break.elapse(12_000, state)

    # then
    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])
    assert dealing_count == 8


def test_thunder_break_decays(
    thunder_break: ThunderBreak, thunder_break_state: ThunderBreakState
):
    # when
    state, _ = thunder_break.use(None, thunder_break_state)
    state, events = thunder_break.elapse(12_000, state)

    # then
    dealing_events = [e for e in events if e.tag == Tag.DAMAGE]
    for idx in range(7):
        assert (
            dealing_events[idx].payload["damage"] * 0.8
            - dealing_events[idx + 1].payload["damage"]
        ) < 1e-8
