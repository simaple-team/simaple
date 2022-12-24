from __future__ import annotations

import pydantic

from simaple.app.application.exception import UnknownSimulatorException
from simaple.app.domain.services.statistics import get_cumulative_logs, get_damage_logs
from simaple.app.domain.simulator import Simulator
from simaple.app.domain.uow import UnitOfWork
from simaple.core.base import Stat
from simaple.simulate.base import Action, Event
from simaple.simulate.component.view import Running, Validity


class PlayLogResponse(pydantic.BaseModel):
    events: list[Event]
    index: int
    validity_view: dict[str, Validity]
    running_view: dict[str, Running]
    buff_view: Stat
    clock: float
    damage: float
    damages: list[tuple[str, float]]
    delay: float
    action: Action
    checkpoint: dict

    @classmethod
    def from_playlog(cls, simulator: Simulator, index: int) -> PlayLogResponse:
        playlog = simulator.history.get(index)
        return PlayLogResponse(
            events=playlog.events,
            index=index,
            validity_view=playlog.view.validity_view,
            running_view=playlog.view.running_view,
            buff_view=playlog.view.get_buff(),
            clock=playlog.clock,
            damages=playlog.get_damages(simulator.calculator),
            damage=playlog.get_total_damage(simulator.calculator),
            delay=playlog.get_delay(),
            action=playlog.action,
            checkpoint=playlog.checkpoint,
        )


def query_latest_playlog(simulator_id: str, uow: UnitOfWork) -> PlayLogResponse:
    simulator = uow.simulator_repository().get(simulator_id)
    if simulator is None:
        raise UnknownSimulatorException()

    latest_index = len(simulator.history) - 1

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
        for log_index in range(len(simulator.history))
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

    cumulative_x, cumulative_y = get_cumulative_logs(simulator.history, simulator)
    value_x, value_y = get_damage_logs(simulator.history, simulator)

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
