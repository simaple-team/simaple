from typing import Any

import fastapi
import pydantic
from dependency_injector.wiring import Provide, inject

from simaple.app.application.command import (
    create_simulator,
    override_checkpint,
    play_action,
    play_elapse,
    play_use,
    play_use_and_elapse,
    rollback,
)
from simaple.app.application.query import (
    PlayLogResponse,
    SimulatorResponse,
    query_all_simulator,
    query_every_playlog,
    query_latest_playlog,
    query_playlog,
)
from simaple.app.domain.simulator_configuration import (
    BaselineConfiguration,
    MinimalSimulatorConfiguration,
)
from simaple.app.domain.uow import UnitOfWork
from simaple.app.interface.container import WebContainer
from simaple.simulate.base import Action

UowProvider = fastapi.Depends(Provide[WebContainer.unit_of_work])
router = fastapi.APIRouter(prefix="/workspaces")


@router.post("/", response_model=SimulatorResponse)
@inject
def create(
    conf: MinimalSimulatorConfiguration,
    uow: UnitOfWork = UowProvider,
) -> Any:
    simulator_id = create_simulator(conf, uow)

    return SimulatorResponse(id=simulator_id)


@router.post("/baseline", response_model=SimulatorResponse)
@inject
def create_from_baseline(
    conf: BaselineConfiguration,
    uow: UnitOfWork = UowProvider,
) -> Any:
    simulator_id = create_simulator(conf, uow)

    return SimulatorResponse(id=simulator_id)


@router.get("/")
@inject
def get_all_simulator(
    uow: UnitOfWork = UowProvider,
) -> list[SimulatorResponse]:
    return query_all_simulator(uow)


@router.post("/play/{simulator_id}", response_model=PlayLogResponse)
@inject
def play(
    simulator_id: str,
    action: Action,
    uow: UnitOfWork = UowProvider,
) -> PlayLogResponse:
    play_action(simulator_id, action, uow)

    return query_latest_playlog(simulator_id, uow)


class RequestDispatchUse(pydantic.BaseModel):
    name: str


@router.post("/use/{simulator_id}", response_model=PlayLogResponse)
@inject
def dispatch_use(
    simulator_id: str,
    request: RequestDispatchUse,
    uow: UnitOfWork = UowProvider,
) -> PlayLogResponse:
    play_use(simulator_id, request.name, uow)

    return query_latest_playlog(simulator_id, uow)


@router.post("/use_and_elapse/{simulator_id}", response_model=PlayLogResponse)
@inject
def dispatch_use_and_elapse(
    simulator_id: str,
    request: RequestDispatchUse,
    uow: UnitOfWork = UowProvider,
) -> PlayLogResponse:
    play_use_and_elapse(simulator_id, request.name, uow)

    return query_latest_playlog(simulator_id, uow)


class RequestDispatchElapse(pydantic.BaseModel):
    time: float


@router.post("/elapse/{simulator_id}", response_model=PlayLogResponse)
@inject
def dispatch_elapse(
    simulator_id: str,
    request: RequestDispatchElapse,
    uow: UnitOfWork = UowProvider,
) -> PlayLogResponse:
    play_elapse(simulator_id, request.time, uow)

    return query_latest_playlog(simulator_id, uow)


@router.get("/logs/{simulator_id}/{log_index}", response_model=PlayLogResponse)
@inject
def get_log(
    simulator_id: str,
    log_index: int,
    uow: UnitOfWork = UowProvider,
) -> PlayLogResponse:
    return query_playlog(simulator_id, log_index, uow)


@router.get("/logs/{simulator_id}", response_model=list[PlayLogResponse])
@inject
def get_all_log(
    simulator_id: str,
    uow: UnitOfWork = UowProvider,
) -> list[PlayLogResponse]:
    return query_every_playlog(simulator_id, uow)


@router.post("/rollback/{simulator_id}/{history_index}", response_model=None)
@inject
def rollback_to_checkpoint(
    simulator_id: str,
    history_index: int,
    uow: UnitOfWork = UowProvider,
) -> None:
    rollback(simulator_id, history_index, uow)


@router.post("/override/{simulator_id}", response_model=None)
@inject
def override(
    simulator_id: str,
    ckpt_json: dict,
    uow: UnitOfWork = UowProvider,
) -> None:
    override_checkpint(simulator_id, ckpt_json, uow)
