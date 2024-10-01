from __future__ import annotations

from typing import Any, TypedDict

from simaple.core.base import Stat
from simaple.simulate.base import Action, AddressedStore, Checkpoint, Event, PlayLog
from simaple.simulate.component.view import Running, Validity
from simaple.simulate.policy.base import Command, OperationLog


class DamageRecord(TypedDict):
    name: str
    damage: float
    hit: float


class DummyCheckpoint(Checkpoint):
    store_ckpt: dict[str, Any] = {}

    def restore(self) -> AddressedStore:
        raise ValueError("DummyCheckpoint cannot be restored")


class PlayLogResponse(TypedDict):
    events: list[Event]
    validity_view: dict[str, Validity]
    running_view: dict[str, Running]
    buff_view: Stat
    clock: float
    delay: float
    action: Action
    checkpoint: Checkpoint | None
    total_damage: float
    damage_records: list[DamageRecord]


def play_log_contains_checkpoint(play_log_response: PlayLogResponse) -> bool:
    return play_log_response["checkpoint"] is not None


def restore_playlog(play_log_response: PlayLogResponse) -> PlayLog:
    if play_log_response["checkpoint"] is None:
        checkpoint: Checkpoint = DummyCheckpoint()
    else:
        checkpoint = play_log_response["checkpoint"]

    return PlayLog(
        events=play_log_response["events"],
        clock=play_log_response["clock"],
        action=play_log_response["action"],
        checkpoint=checkpoint,
    )


class OperationLogResponse(TypedDict):
    logs: list[PlayLogResponse]
    hash: str
    previous_hash: str
    command: Command
    index: int
    description: str | None


def restore_operation_log(operation_log_response: OperationLogResponse) -> OperationLog:
    return OperationLog(
        command=operation_log_response["command"],
        playlogs=[restore_playlog(log) for log in operation_log_response["logs"]],
        previous_hash=operation_log_response["previous_hash"],
        description=operation_log_response["description"],
    )


def operation_log_contains_checkpoint(
    operation_log_response: OperationLogResponse,
) -> bool:
    return (
        all(play_log_contains_checkpoint(log) for log in operation_log_response["logs"])
        and len(operation_log_response["logs"]) > 0
    )
