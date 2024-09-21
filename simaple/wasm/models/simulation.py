from __future__ import annotations

import pydantic

from simaple.core.base import Stat
from simaple.simulate.base import Action, Checkpoint, Event, PlayLog
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
    checkpoint: Checkpoint
    total_damage: float
    damage_records: list[DamageRecord]

    def restore_playlog(self) -> PlayLog:
        return PlayLog(
            events=self.events,
            clock=self.clock,
            action=self.action,
            checkpoint=self.checkpoint,
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
