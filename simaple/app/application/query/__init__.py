from __future__ import annotations

import pydantic

from simaple.app.application.exception import UnknownSimulatorException
from simaple.app.domain.services.statistics import get_cumulative_logs, get_damage_logs
from simaple.app.domain.simulator import Simulator
from simaple.app.domain.uow import UnitOfWork
from simaple.core.base import Stat
from simaple.simulate.base import Action, Checkpoint, Event
from simaple.simulate.component.view import Running, Validity
from simaple.simulate.policy.base import Operation
from simaple.simulate.report.base import DamageLog, Report


class PlayLogResponse(pydantic.BaseModel):
    events: list[Event]
    validity_view: dict[str, Validity]
    running_view: dict[str, Running]
    buff_view: Stat
    report: Report
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
    def from_simulator(cls, simulator: Simulator, index: int) -> OperationLogResponse:
        if index < 0:
            index += len(simulator.engine.history())

        operation_log = simulator.engine.history().get(index)

        playlog_responses = []

        for playlog, viewer in simulator.engine.inspect(operation_log):
            report = Report(
                time_series=[simulator.engine.get_simulation_entry(playlog)]
            )
            damage_logs: list[DamageLog] = sum(
                [entry.damage_logs for entry in report.entries()], []
            )
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
                    report=report,
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


def query_latest_operation_log(
    simulator_id: str, uow: UnitOfWork
) -> OperationLogResponse:
    simulator = uow.simulator_repository().get(simulator_id)
    if simulator is None:
        raise UnknownSimulatorException()

    latest_index = len(simulator.engine.history()) - 1

    return OperationLogResponse.from_simulator(simulator, latest_index)


def query_operation_log(
    simulator_id: str, log_index: int, uow: UnitOfWork
) -> OperationLogResponse:
    simulator = uow.simulator_repository().get(simulator_id)

    if simulator is None:
        raise UnknownSimulatorException()

    return OperationLogResponse.from_simulator(simulator, log_index)


def query_every_opration_log(
    simulator_id: str, uow: UnitOfWork
) -> list[OperationLogResponse]:
    simulator = uow.simulator_repository().get(simulator_id)

    if simulator is None:
        raise UnknownSimulatorException()

    return [
        OperationLogResponse.from_simulator(simulator, log_index)
        for log_index in range(simulator.engine.length())
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

    cumulative_x, cumulative_y = get_cumulative_logs(simulator.engine, simulator)
    value_x, value_y = get_damage_logs(simulator.engine, simulator)

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
