import pytest

from simaple.simulate.base import Checkpoint, PlayLog
from simaple.simulate.policy.base import Operation, OperationLog, SimulationHistory


@pytest.fixture(name="history_use_playlog")
def fixture_history_use_playlog():
    return PlayLog(
        action={"name": "A", "method": "use", "payload": None},
        events=[
            {"name": "A", "payload": {}, "method": "use", "tag": None, "handler": None}
        ],
        clock=3000.0,
        checkpoint=Checkpoint(store_ckpt={}),
    )


@pytest.fixture(name="history_elapse_playlog")
def fixture_history_elapse_playlog():
    return PlayLog(
        action={"name": "A", "method": "use", "payload": None},
        events=[
            {
                "name": "A",
                "payload": {"time": 800},
                "method": "elapse",
                "tag": "global.delay",
                "handler": None,
            }
        ],
        clock=3000.0,
        checkpoint=Checkpoint(store_ckpt={}),
    )


def test_no_delay(history_use_playlog: PlayLog):
    assert history_use_playlog.get_delay_left() == 0


def test_yes_delay(history_elapse_playlog: PlayLog):
    assert history_elapse_playlog.get_delay_left() == 800


def test_playlog(history_use_playlog, history_elapse_playlog):
    OperationLog(
        command=Operation(command="cast", name="test"),
        playlogs=[
            history_use_playlog,
            history_elapse_playlog,
        ],
        previous_hash="",
    )


def test_get_hash(history_use_playlog, history_elapse_playlog):
    history = SimulationHistory(logs=[])
    history.commit(
        Operation(command="use", name="test"),
        [history_use_playlog],
    )
    history.commit(
        Operation(command="elapse", name="test"),
        [history_elapse_playlog],
    )

    this_hash = history.get(1).hash

    assert history.get_hash_index(this_hash) == 1
