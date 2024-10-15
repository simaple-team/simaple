import pytest

from simaple.simulate.component.specific.dualblade import (
    FinalCutComponent,
    FinalCutState,
)
from simaple.simulate.global_property import Dynamics


@pytest.fixture(name="final_cut")
def fixture_final_cut():
    return FinalCutComponent(
        id="test",
        name="test-final-cut",
        cooldown_duration=90000,
        delay=450,
        damage=2000,
        hit=1,
        sudden_raid_cooltime_reduce=20,
    )


@pytest.fixture(name="final_cut_state")
def fixture_final_cut_state(final_cut: FinalCutComponent, dynamics: Dynamics):
    return {**final_cut.get_default_state(), "dynamics": dynamics}


def test_cooltime_reduce(final_cut: FinalCutComponent, final_cut_state: FinalCutState):
    # given
    state, _ = final_cut.use(None, final_cut_state)

    # when
    state, _ = final_cut.sudden_raid(None, state)

    # then
    assert final_cut.validity(state).time_left == 72000


def test_cooltime_reduce_after_elapse(
    final_cut: FinalCutComponent, final_cut_state: FinalCutState
):
    # given
    state, _ = final_cut.use(None, final_cut_state)

    # when
    state, _ = final_cut.elapse(80000, state)
    state, _ = final_cut.sudden_raid(None, state)

    # then
    assert final_cut.validity(state).time_left == 8000
