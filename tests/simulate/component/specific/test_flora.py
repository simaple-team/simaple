import pytest

from simaple.core.base import Stat
from simaple.simulate.component.specific.flora import (
    MagicCurcuitFullDriveComponent,
    MagicCurcuitFullDriveState,
)
from simaple.simulate.global_property import Dynamics
from simaple.simulate.reserved_names import Tag


@pytest.fixture(name="magic_curcuit_full_drive")
def fixture_magic_curcuit_full_drive():
    return MagicCurcuitFullDriveComponent(
        id="test",
        name="매직 서킷 풀드라이브",
        cooldown_duration=200_000,
        delay=540,
        periodic_damage=1100,
        periodic_hit=3,
        periodic_interval=4000,
        lasting_duration=60_000,
        max_damage_multiplier=50,
    )


@pytest.fixture(name="magic_curcuit_full_drive_state")
def fixture_magic_curcuit_full_drive_state(
    magic_curcuit_full_drive: MagicCurcuitFullDriveComponent, dynamics: Dynamics
):
    return MagicCurcuitFullDriveState.model_validate(
        {**magic_curcuit_full_drive.get_default_state(), "dynamics": dynamics}
    )


def test_magic_curcuit_buff(
    magic_curcuit_full_drive: MagicCurcuitFullDriveComponent,
    magic_curcuit_full_drive_state: MagicCurcuitFullDriveState,
):
    state, _ = magic_curcuit_full_drive.use(None, magic_curcuit_full_drive_state)

    assert magic_curcuit_full_drive.buff(state) == Stat(damage_multiplier=50)


def test_magic_curcuit_stop(
    magic_curcuit_full_drive: MagicCurcuitFullDriveComponent,
    magic_curcuit_full_drive_state: MagicCurcuitFullDriveState,
):
    state, _ = magic_curcuit_full_drive.use(None, magic_curcuit_full_drive_state)
    state, _ = magic_curcuit_full_drive.elapse(60_000, state)

    assert magic_curcuit_full_drive.buff(state) is None


def test_magic_curcuit_tick_count(
    magic_curcuit_full_drive: MagicCurcuitFullDriveComponent,
    magic_curcuit_full_drive_state: MagicCurcuitFullDriveState,
):
    state, _ = magic_curcuit_full_drive.use(None, magic_curcuit_full_drive_state)
    state, events = magic_curcuit_full_drive.elapse(60_000, state)

    dealing_event = [e for e in events if e.tag == Tag.DAMAGE]

    assert len(dealing_event) == 14
