from typing import Any

import fastapi
import pydantic
from fastapi import Depends

from simaple.app.application.command import (
    create_workspace,
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
from simaple.app.domain.services.workspace_builder import WorkspaceConfiguration
from simaple.app.domain.uow import UnitOfWork
from simaple.app.interface.base import get_unit_of_work
from simaple.simulate.base import Action

router = fastapi.APIRouter(prefix="/workspaces")


class WorkspaceResponse(pydantic.BaseModel):
    id: str


@router.post("", response_model=WorkspaceResponse)
def create(
    conf: WorkspaceConfiguration,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> Any:
    workspace_id = create_workspace(conf, uow)

    return WorkspaceResponse(id=workspace_id)


@router.post("/play/{workspace_id}", response_model=PlayLogResponse)
def play(
    workspace_id: str,
    action: Action,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> PlayLogResponse:
    play_action(workspace_id, action, uow)

    return query_latest_playlog(workspace_id, uow)


class RequestDispatchUse(pydantic.BaseModel):
    name: str


@router.post("/use/{workspace_id}", response_model=PlayLogResponse)
def dispatch_use(
    workspace_id: str,
    request: RequestDispatchUse,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> PlayLogResponse:
    play_use(workspace_id, request.name, uow)

    return query_latest_playlog(workspace_id, uow)


@router.post("/use_and_elapse/{workspace_id}", response_model=PlayLogResponse)
def dispatch_use_and_elapse(
    workspace_id: str,
    request: RequestDispatchUse,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> PlayLogResponse:
    play_use_and_elapse(workspace_id, request.name, uow)

    return query_latest_playlog(workspace_id, uow)


class RequestDispatchElapse(pydantic.BaseModel):
    time: float


@router.post("/elapse/{workspace_id}", response_model=PlayLogResponse)
def dispatch_elapse(
    workspace_id: str,
    request: RequestDispatchElapse,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> PlayLogResponse:
    play_elapse(workspace_id, request.time, uow)

    return query_latest_playlog(workspace_id, uow)


@router.get("/logs/{workspace_id}/{log_index}", response_model=PlayLogResponse)
def get_log(
    workspace_id: str,
    log_index: int,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> PlayLogResponse:
    return query_playlog(workspace_id, log_index, uow)
