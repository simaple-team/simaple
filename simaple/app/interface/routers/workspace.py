from typing import Any

import fastapi
import pydantic
from dependency_injector.wiring import Provide, inject

from simaple.app.application.command.simulator import (
    create_from_plan,
    create_simulator,
    play_operation,
    rollback,
    run_plan,
)
from simaple.app.application.query import (
    OperationLogResponse,
    SimulatorResponse,
    query_all_simulator,
    query_every_opration_log,
    query_latest_operation_log,
    query_operation_log,
)
from simaple.app.domain.uow import UnitOfWork
from simaple.app.interface.container import WebContainer
from simaple.simulate.interface.simulator_configuration import (
    BaselineConfiguration,
    MinimalSimulatorConfiguration,
)

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


class RequestCreateFromPlan(pydantic.BaseModel):
    plan: str


@router.post("/plan", response_model=SimulatorResponse)
@inject
def create_from_simulator(
    request: RequestCreateFromPlan,
    uow: UnitOfWork = UowProvider,
) -> Any:
    simulator_id = create_from_plan(request.plan, uow)

    return SimulatorResponse(id=simulator_id)


@router.get("/")
@inject
def get_all_simulator(
    uow: UnitOfWork = UowProvider,
) -> list[SimulatorResponse]:
    return query_all_simulator(uow)


class RequestPlay(pydantic.BaseModel):
    operation: str


@router.post("/play/{simulator_id}", response_model=OperationLogResponse)
@inject
def play(
    simulator_id: str,
    request: RequestPlay,
    uow: UnitOfWork = UowProvider,
) -> OperationLogResponse:
    play_operation(simulator_id, request.operation, uow)

    return query_latest_operation_log(simulator_id, uow)


class RequestRunPlan(pydantic.BaseModel):
    plan: str


@router.post("/run/{simulator_id}")
@inject
def run(
    simulator_id: str,
    request: RequestRunPlan,
    uow: UnitOfWork = UowProvider,
) -> list[OperationLogResponse]:
    run_plan(simulator_id, request.plan, uow)

    return query_every_opration_log(simulator_id, uow)


class RequestDispatchUse(pydantic.BaseModel):
    name: str


class RequestDispatchElapse(pydantic.BaseModel):
    time: float


@router.get("/logs/{simulator_id}/latest", response_model=OperationLogResponse)
@inject
def get_latest_log(
    simulator_id: str,
    uow: UnitOfWork = UowProvider,
) -> OperationLogResponse:
    return query_operation_log(simulator_id, -1, uow)


@router.get("/logs/{simulator_id}/{log_index}", response_model=OperationLogResponse)
@inject
def get_log(
    simulator_id: str,
    log_index: int,
    uow: UnitOfWork = UowProvider,
) -> OperationLogResponse:
    return query_operation_log(simulator_id, log_index, uow)


@router.get("/logs/{simulator_id}", response_model=list[OperationLogResponse])
@inject
def get_all_log(
    simulator_id: str,
    uow: UnitOfWork = UowProvider,
) -> list[OperationLogResponse]:
    return query_every_opration_log(simulator_id, uow)


@router.post("/rollback/{simulator_id}/{history_index}", response_model=None)
@inject
def rollback_to_checkpoint(
    simulator_id: str,
    history_index: int,
    uow: UnitOfWork = UowProvider,
) -> None:
    rollback(simulator_id, history_index, uow)
