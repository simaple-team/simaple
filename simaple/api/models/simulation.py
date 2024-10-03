from __future__ import annotations

from typing import Any

import pydantic

from simaple.core.base import Stat
from simaple.simulate.base import Action, AddressedStore, Checkpoint, Event, PlayLog
from simaple.simulate.component.view import Running, Validity
from simaple.simulate.policy.base import Command, OperationLog
from simaple.simulate.report.base import SimulationEntry


class _Report(pydantic.BaseModel):
    """
    For backward Compat. only (this is redundant)
    """

    model_config = pydantic.ConfigDict(extra="forbid")

    time_series: list[SimulationEntry]


class DamageRecord(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    name: str
    damage: float
    hit: float


class DummyCheckpoint(Checkpoint):
    store_ckpt: dict[str, Any] = {}

    def restore(self) -> AddressedStore:
        raise ValueError("DummyCheckpoint cannot be restored")


class PlayLogResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    events: list[Event]
    validity_view: dict[str, Validity]
    running_view: dict[str, Running]
    buff_view: Stat
    report: _Report
    clock: float
    delay: float
    action: Action
    checkpoint: Checkpoint | None
    total_damage: float
    damage_records: list[DamageRecord]

    def contains_chekcpoint(self) -> bool:
        return self.checkpoint is not None

    def restore_playlog(self) -> PlayLog:
        if self.checkpoint is None:
            checkpoint: Checkpoint = DummyCheckpoint()
        else:
            checkpoint = self.checkpoint

        return PlayLog(
            events=self.events,
            clock=self.clock,
            action=self.action,
            checkpoint=checkpoint,
        )


class OperationLogResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    logs: list[PlayLogResponse]
    hash: str
    previous_hash: str
    command: Command
    index: int
    description: str | None

    def restore_operation_log(self) -> OperationLog:
        return OperationLog(
            command=self.command,
            playlogs=[log.restore_playlog() for log in self.logs],
            previous_hash=self.previous_hash,
            description=self.description,
        )

    def contains_chekcpoint(self) -> bool:
        return (
            all(log.contains_chekcpoint() for log in self.logs) and len(self.logs) > 0
        )
