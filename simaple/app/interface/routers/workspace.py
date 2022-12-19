from typing import Any

import fastapi
import pydantic
from fastapi import Depends

from simaple.app.application.command import (
    create_simulator,
    play_action,
    play_elapse,
    play_use,
    play_use_and_elapse,
)
from simaple.app.application.query import (
    PlayLogResponse,
    query_latest_playlog,
    query_playlog,
)
from simaple.app.domain.simulator_configuration import MinimalSimulatorConfiguration
from simaple.app.domain.uow import UnitOfWork
from simaple.app.interface.base import get_unit_of_work
from simaple.simulate.base import Action

router = fastapi.APIRouter(prefix="/workspaces")


class SimulatorResponse(pydantic.BaseModel):
    id: str


@router.post("", response_model=SimulatorResponse)
def create(
    conf: MinimalSimulatorConfiguration,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> Any:
    simulator_id = create_simulator(conf, uow)

    return SimulatorResponse(id=simulator_id)


@router.post("/play/{simulator_id}", response_model=PlayLogResponse)
def play(
    simulator_id: str,
    action: Action,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> PlayLogResponse:
    play_action(simulator_id, action, uow)

    return query_latest_playlog(simulator_id, uow)


class RequestDispatchUse(pydantic.BaseModel):
    name: str


@router.post("/use/{simulator_id}", response_model=PlayLogResponse)
def dispatch_use(
    simulator_id: str,
    request: RequestDispatchUse,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> PlayLogResponse:
    play_use(simulator_id, request.name, uow)

    return query_latest_playlog(simulator_id, uow)


@router.post("/use_and_elapse/{simulator_id}", response_model=PlayLogResponse)
def dispatch_use_and_elapse(
    simulator_id: str,
    request: RequestDispatchUse,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> PlayLogResponse:
    play_use_and_elapse(simulator_id, request.name, uow)

    return query_latest_playlog(simulator_id, uow)


class RequestDispatchElapse(pydantic.BaseModel):
    time: float


@router.post("/elapse/{simulator_id}", response_model=PlayLogResponse)
def dispatch_elapse(
    simulator_id: str,
    request: RequestDispatchElapse,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> PlayLogResponse:
    play_elapse(simulator_id, request.time, uow)

    return query_latest_playlog(simulator_id, uow)


@router.get("/logs/{simulator_id}/{log_index}", response_model=PlayLogResponse)
def get_log(
    simulator_id: str,
    log_index: int,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> PlayLogResponse:
    return query_playlog(simulator_id, log_index, uow)
