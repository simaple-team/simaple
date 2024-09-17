from __future__ import annotations

import pydantic

from simaple.core.base import Stat
from simaple.simulate.base import Action, Checkpoint, Event
from simaple.simulate.component.view import Running, Validity
from simaple.simulate.engine import OperationEngine
from simaple.simulate.policy.base import Operation
from simaple.simulate.report.base import DamageLog, SimulationEntry


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

    @classmethod
    def from_simulator(
        cls, engine: OperationEngine, index: int
    ) -> OperationLogResponse:
        if index < 0:
            index += len(engine.history())

        operation_log = engine.history().get(index)

        playlog_responses = []

        for playlog in operation_log.playlogs:
            viewer = engine.get_viewer(playlog)
            entry = engine.get_simulation_entry(playlog)
            damage_logs: list[DamageLog] = entry.damage_logs

            damages = [
                (damage_log.name, damage_log.damage) for damage_log in damage_logs
            ]
            damage = sum([damage_log.damage for damage_log in damage_logs])
            playlog_responses.append(
                PlayLogResponse(
                    events=playlog.events,
                    validity_view={v.name: v for v in viewer("validity")},
                    running_view={v.name: v for v in viewer("running")},
                    buff_view=viewer("buff"),
                    clock=playlog.clock,
                    report=_Report(time_series=[entry]),
                    delay=playlog.get_delay_left(),
                    action=playlog.action,
                    checkpoint=playlog.checkpoint,
                    damage=damage,
                    damages=damages,
                )
            )

        return OperationLogResponse(
            index=index,
            logs=playlog_responses,
            hash=operation_log.hash,
            previous_hash=operation_log.previous_hash,
            operation=operation_log.operation,
        )
