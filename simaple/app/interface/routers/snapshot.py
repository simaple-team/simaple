import fastapi
import pydantic
from dependency_injector.wiring import Provide, inject

from simaple.app.application.command.snapshot import create_snapshot, load_from_snapshot
from simaple.app.application.query.snapshot import SnapshotResponse, query_all_snapshot
from simaple.app.domain.uow import UnitOfWork
from simaple.app.interface.container import WebContainer

UowProvider = fastapi.Depends(Provide[WebContainer.unit_of_work])

snapshot_router = fastapi.APIRouter(prefix="/snapshots")


@snapshot_router.get("/", response_model=list[SnapshotResponse])
@inject
def get_all_snapshots(
    uow: UnitOfWork = UowProvider,
) -> list[SnapshotResponse]:
    return query_all_snapshot(uow)


class CreateSnapshotCommand(pydantic.BaseModel):
    simulator_id: str
    name: str


@snapshot_router.post("/", response_model=None)
@inject
def post_create_snapshot(
    snapshot_create_command: CreateSnapshotCommand,
    uow: UnitOfWork = UowProvider,
):
    create_snapshot(
        snapshot_create_command.simulator_id, snapshot_create_command.name, uow
    )


@snapshot_router.post("/{snapshot_id}/load", response_model=str)
@inject
def post_load_from_snapshot(
    snapshot_id: str,
    uow: UnitOfWork = UowProvider,
) -> str:
    return load_from_snapshot(snapshot_id, uow)
