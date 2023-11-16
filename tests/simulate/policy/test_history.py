import pytest

from simaple.simulate.base import Action, Checkpoint, Client, Event, ViewerType
from simaple.simulate.policy.base import (
    BehaviorGenerator,
    Operation,
    OperationLog,
    PlayLog,
)
from simaple.simulate.reserved_names import Tag


@pytest.fixture
def history_use_playlog():
    return PlayLog(
        action={"name": "A", "method": "use", "payload": None},
        events=[
            {"name": "A", "payload": {}, "method": "use", "tag": None, "handler": None}
        ],
        clock=3000.0,
        checkpoint=Checkpoint(store_ckpt={}, callbacks=[]),
    )


@pytest.fixture
def history_elapse_playlog():
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
        checkpoint=Checkpoint(store_ckpt={}, callbacks=[]),
    )


def test_no_delay(history_use_playlog: PlayLog):
    assert history_use_playlog.get_delay_left() == 0


def test_yes_delay(history_elapse_playlog: PlayLog):
    assert history_elapse_playlog.get_delay_left() == 800


def test_playlog(history_use_playlog, history_elapse_playlog):
    op_log = OperationLog(
        operation=Operation(command="cast", name="test"),
        playlogs=[
            history_use_playlog,
            history_elapse_playlog,
        ],
        previous_hash="",
    )
