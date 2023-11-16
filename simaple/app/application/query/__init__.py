from __future__ import annotations

import pydantic

from simaple.app.application.exception import UnknownSimulatorException
from simaple.app.domain.services.statistics import get_cumulative_logs, get_damage_logs
from simaple.app.domain.simulator import Simulator
from simaple.app.domain.uow import UnitOfWork
from simaple.core.base import Stat
from simaple.simulate.base import Action, Checkpoint, Event
from simaple.simulate.component.view import Running, Validity
from simaple.simulate.policy.base import Operation, PlayLog, SimulationShell, ViewerType
from simaple.simulate.report.base import Report


class _SinglePlayLogResponse(pydantic.BaseModel):
    events: list[Event]
    validity_view: dict[str, Validity]
    running_view: dict[str, Running]
    buff_view: Stat
    report: Report
    clock: float
    delay: float
    action: Action
    checkpoint: Checkpoint

    @classmethod
    def from_playlog(
        cls, playlog: PlayLog, shell: SimulationShell
    ) -> _SinglePlayLogResponse:
        playlog_viewer = shell.get_viewer(playlog)

        return _SinglePlayLogResponse(
            events=playlog.events,
            validity_view={v.name: v for v in playlog_viewer("validity")},
            running_view={v.name: v for v in playlog_viewer("running")},
            buff_view=playlog_viewer("buff"),
            clock=playlog.clock,
            report=shell.get_report(playlog),
            delay=playlog.get_delay_left(),
            action=playlog.action,
            checkpoint=playlog.checkpoint,
        )


class PlayLogResponse(pydantic.BaseModel):
    logs: list[_SinglePlayLogResponse]
    hash: str
    previous_hash: str
    operation: Operation
    index: int

    @classmethod
    def from_playlog(cls, simulator: Simulator, index: int) -> PlayLogResponse:
        if index < 0:
            index += simulator.shell.length()

        operation_log = simulator.shell.get(index)
        return PlayLogResponse(
            index=index,
            logs=[
                _SinglePlayLogResponse.from_playlog(playlog, simulator.shell)
                for playlog in operation_log.playlogs
            ],
            hash=operation_log.hash,
            previous_hash=operation_log.previous_hash,
            operation=operation_log.operation,
        )


def query_latest_playlog(simulator_id: str, uow: UnitOfWork) -> PlayLogResponse:
    simulator = uow.simulator_repository().get(simulator_id)
    if simulator is None:
        raise UnknownSimulatorException()

    latest_index = simulator.shell.length() - 1

    return PlayLogResponse.from_playlog(simulator, latest_index)


def query_playlog(
    simulator_id: str, log_index: int, uow: UnitOfWork
) -> PlayLogResponse:
    simulator = uow.simulator_repository().get(simulator_id)

    if simulator is None:
        raise UnknownSimulatorException()

    return PlayLogResponse.from_playlog(simulator, log_index)


def query_every_playlog(simulator_id: str, uow: UnitOfWork) -> list[PlayLogResponse]:
    simulator = uow.simulator_repository().get(simulator_id)

    if simulator is None:
        raise UnknownSimulatorException()

    return [
        PlayLogResponse.from_playlog(simulator, log_index)
        for log_index in range(simulator.shell.length())
    ]


class StatisticsResponse(pydantic.BaseModel):
    cumulative_x: list[float]
    cumulative_y: list[float]
    value_x: list[float]
    value_y: list[float]


def query_statistics(simulator_id: str, uow: UnitOfWork) -> StatisticsResponse:
    simulator = uow.simulator_repository().get(simulator_id)

    if simulator is None:
        raise UnknownSimulatorException()

    cumulative_x, cumulative_y = get_cumulative_logs(simulator.shell, simulator)
    value_x, value_y = get_damage_logs(simulator.shell, simulator)

    return StatisticsResponse(
        cumulative_x=cumulative_x,
        cumulative_y=cumulative_y,
        value_x=value_x,
        value_y=value_y,
    )


class SimulatorResponse(pydantic.BaseModel):
    id: str


def query_all_simulator(uow: UnitOfWork) -> list[SimulatorResponse]:
    simulators = uow.simulator_repository().get_all()

    return [SimulatorResponse(id=simulator.id) for simulator in simulators]
