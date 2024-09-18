from __future__ import annotations

import pydantic

from simaple.core.base import Stat
from simaple.simulate.base import Action, Checkpoint, Event
from simaple.simulate.component.view import Running, Validity
from simaple.simulate.policy.base import Operation
from simaple.simulate.report.base import SimulationEntry


class _Report(pydantic.BaseModel):
    """
    For backward Compat. only (this is redundant)
    """

    time_series: list[SimulationEntry]


class PlayLogResponse(pydantic.BaseModel):
    events: list[Event]
    validity_view: dict[str, Validity]
    running_view: dict[str, Running]
    buff_view: Stat
    report: _Report
    clock: float
    delay: float
    action: Action
    checkpoint: Checkpoint
    damage: float
    damages: list[tuple[str, float]]


class OperationLogResponse(pydantic.BaseModel):
    logs: list[PlayLogResponse]
    hash: str
    previous_hash: str
    operation: Operation
    index: int
